import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import numpy as np

# Load env variables
load_dotenv()

# Setup paths
FAISS_INDEX_PATH = "./data/faiss.index"
FAISS_META_PATH = "./data/faiss_meta.json"
NUMPY_EMBED_PATH = "./data/embeddings.npy"

# Ensure output directory exists
os.makedirs("./data", exist_ok=True)

# Safe FAISS Import Fallback
try:
    import faiss
    FAISS_AVAILABLE = True
    print("FAISS is available.")
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS is NOT available. Falling back to NumPy format.")

# Lazy-initialization function for sentence-transformer model
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        model_name = os.getenv('EMBED_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        from sentence_transformers import SentenceTransformer
        print(f"Loading embedding model: {model_name}...")
        _embed_model = SentenceTransformer(model_name)
    return _embed_model

def build_vector_database():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db = client['citizen_portal']
    services_col = db['services']

    services = list(services_col.find({}))
    if not services:
        print("No services found in database! Please run seed_data.py first.")
        return

    texts = []
    metadata = []

    for s in services:
        m_id = s.get('id', '')
        m_name = s.get('name', {})
        m_contact = s.get('contact', {})
        m_links = s.get('links', [])
        
        for sub in s.get('subservices', []):
            sub_id = sub.get('id', '')
            sub_name = sub.get('name', {})
            
            for q_obj in sub.get('questions', []):
                q_en = q_obj.get('q', {}).get('en', '')
                q_si = q_obj.get('q', {}).get('si', '')
                q_ta = q_obj.get('q', {}).get('ta', '')
                ans_en = q_obj.get('answer', {}).get('en', '')
                ans_si = q_obj.get('answer', {}).get('si', '')
                ans_ta = q_obj.get('answer', {}).get('ta', '')
                
                if not q_en:
                    continue
                
                # Combine fields for rich semantic representation
                text_representation = f"{q_en} Subservice: {sub_name.get('en', '')}. Ministry: {m_name.get('en', '')}."
                texts.append(text_representation)
                
                metadata.append({
                    "ministry_id": m_id,
                    "ministry_name": m_name,
                    "ministry_contact": m_contact,
                    "ministry_links": m_links,
                    "subservice_id": sub_id,
                    "subservice_name": sub_name,
                    "q": {"en": q_en, "si": q_si, "ta": q_ta},
                    "answer": {"en": ans_en, "si": ans_si, "ta": ans_ta}
                })

    if not texts:
        print("No questions found to index.")
        return

    print(f"Generating embeddings for {len(texts)} questions...")
    model = get_embed_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Save Metadata JSON
    with open(FAISS_META_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Saved metadata to {FAISS_META_PATH}")

    # Save Index
    if FAISS_AVAILABLE:
        dimension = embeddings.shape[1]
        # Using IndexFlatIP (Inner Product) with normalized vectors for Cosine Similarity
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / (norms + 1e-10)
        
        index = faiss.IndexFlatIP(dimension)
        index.add(normalized_embeddings)
        faiss.write_index(index, FAISS_INDEX_PATH)
        print(f"Saved FAISS index to {FAISS_INDEX_PATH}")
    else:
        # Save as raw numpy array
        np.save(NUMPY_EMBED_PATH, embeddings)
        print(f"Saved raw embeddings to {NUMPY_EMBED_PATH}")

    print("Vector database indexing complete!")

if __name__ == "__main__":
    build_vector_database()
