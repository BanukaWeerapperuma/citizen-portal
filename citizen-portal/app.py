import os
import json
import numpy as np
import bcrypt
from flask import Flask, request, jsonify, render_template, send_file, session
import csv
import io
from flask_cors import CORS
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId
import google.generativeai as genai
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime
import logging

# 1. Initialize Flask & App Configurations
load_dotenv()

# Read from environment variables with default fallbacks
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
flask_secret = os.getenv('FLASK_SECRET', 'dev-secret')

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

app = Flask(__name__)
app.secret_key = flask_secret
CORS(app)

# Safe FAISS Import Fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

# FAISS Configuration Paths
FAISS_INDEX_PATH = "./data/faiss.index"
FAISS_META_PATH = "./data/faiss_meta.json"

# Lazy-initialization function for sentence-transformer model
_embed_model = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        model_name = os.getenv('EMBED_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(model_name)
    return _embed_model

@app.route('/api/ping')
def ping():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()})

# 2. Connect to MongoDB (citizen_portal database)
client = MongoClient(mongo_uri)
db = client['citizen_portal']

# Collections
services_col = db['services']
admins_col = db['admins']
engagement_col = db['engagements']  # mapped to db['engagements'] for metrics logging
categories_col = db['categories']
officers_col = db['officers']
ads_col = db['ads']
users_col = db['users']

def build_vector_index():
    services = list(services_col.find({}))
    if not services:
        return 0, FAISS_AVAILABLE

    texts = []
    metadata = []

    for s in services:
        service_id = s.get('id', '')
        service_name = s.get('name', {}).get('en', '')

        for sub in s.get('subservices', []):
            subservice_id = sub.get('id', '')
            subservice_name = sub.get('name', {}).get('en', '')

            for q_obj in sub.get('questions', []):
                question_text = q_obj.get('q', {}).get('en', '')
                answer_text = q_obj.get('answer', {}).get('en', '')

                if not question_text:
                    continue

                content = f"{service_name} | {subservice_name} | {question_text} | {answer_text}"
                texts.append(content)

                metadata.append({
                    "service_id": service_id,
                    "subservice_id": subservice_id,
                    "title": question_text,
                    "downloads": q_obj.get('downloads'),
                    "location": q_obj.get('location'),
                    "instructions": q_obj.get('instructions'),
                    "content": content
                })

    if not texts:
        return 0, FAISS_AVAILABLE

    model = get_embed_model()
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype('float32')

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_embeddings = np.divide(embeddings, norms, out=np.zeros_like(embeddings), where=norms > 0)

    os.makedirs("./data", exist_ok=True)

    if FAISS_AVAILABLE:
        dimension = normalized_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(normalized_embeddings)
        faiss.write_index(index, FAISS_INDEX_PATH)
    else:
        np.save("./data/embeddings.npy", normalized_embeddings)

    with open(FAISS_META_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return len(texts), FAISS_AVAILABLE

def search_vectors(query, top_k=5):
    model = get_embed_model()
    query_vector = model.encode(query)
    query_vector = np.array(query_vector).astype('float32')

    norm = np.linalg.norm(query_vector)
    if norm > 0:
        query_vector = query_vector / norm
    else:
        query_vector = np.zeros_like(query_vector)

    metadata = []
    if os.path.exists(FAISS_META_PATH):
        try:
            with open(FAISS_META_PATH, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            app.logger.error(f"Error loading faiss metadata: {str(e)}")

    if not metadata:
        return []

    hits = []

    if FAISS_AVAILABLE and os.path.exists(FAISS_INDEX_PATH):
        try:
            index = faiss.read_index(FAISS_INDEX_PATH)
            D, I = index.search(np.array([query_vector]).astype('float32'), top_k)
            for idx, score in zip(I[0], D[0]):
                if idx != -1 and idx < len(metadata):
                    hits.append({
                        "metadata": metadata[idx],
                        "score": float(score)
                    })
            return hits
        except Exception as e:
            app.logger.error(f"FAISS search failed, falling back to NumPy: {str(e)}")

    embeddings_npy_path = "./data/embeddings.npy"
    if os.path.exists(embeddings_npy_path):
        try:
            embeddings = np.load(embeddings_npy_path)
            scores = embeddings @ query_vector
            indices = np.argsort(scores)[::-1][:top_k]
            for idx in indices:
                if idx < len(metadata):
                    hits.append({
                        "metadata": metadata[idx],
                        "score": float(scores[idx])
                    })
        except Exception as e:
            app.logger.error(f"NumPy vector search failed: {str(e)}")

    return hits

# 3. Security: admin_required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        admin_pwd = "admin123"
        if not auth_header or auth_header != f"Bearer {admin_pwd}":
            return jsonify({"error": "Unauthorized. Admin access required."}), 401
        return f(*args, **kwargs)
    return decorated_function

# 4. Auto-Setup: Create default admin
def setup_admin():
    if admins_col.count_documents({}) == 0:
        admin_user = "admin"
        admin_pwd = os.getenv('ADMIN_PWD', 'admin123')
        hashed = bcrypt.hashpw(admin_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admins_col.update_one(
            {"username": admin_user},
            {"$set": {"password": hashed, "role": "superadmin"}},
            upsert=True
        )
        print(f"Admin user '{admin_user}' verified/created with hashed password.")

# Run setup
setup_admin()

# 5. Frontend Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# 6. Auth Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    if users_col.find_one({"username": data['username']}):
        return jsonify({"error": "User already exists"}), 400
    users_col.insert_one(data)
    return jsonify({"message": "User created"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = users_col.find_one({"username": data['username'], "password": data['password']})
    if user:
        return jsonify({"message": "Login successful", "username": user['username']}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/admin/login', methods=['POST'])
def admin_login_form():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    admin = admins_col.find_one({"username": username})
    if not admin:
        return jsonify({"error": "Invalid credentials"}), 401

    hashed_pwd = admin.get('password', '')
    if isinstance(hashed_pwd, str) and (hashed_pwd.startswith('$2b$') or hashed_pwd.startswith('$2a$')):
        try:
            password_matched = bcrypt.checkpw(password.encode('utf-8'), hashed_pwd.encode('utf-8'))
        except Exception:
            password_matched = False
    else:
        password_matched = (hashed_pwd == password)

    if password_matched:
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    admin = admins_col.find_one({"username": username})
    if not admin:
        return jsonify({"error": "Invalid credentials"}), 401

    hashed_pwd = admin.get('password', '')
    if isinstance(hashed_pwd, str) and (hashed_pwd.startswith('$2b$') or hashed_pwd.startswith('$2a$')):
        try:
            password_matched = bcrypt.checkpw(password.encode('utf-8'), hashed_pwd.encode('utf-8'))
        except Exception:
            password_matched = False
    else:
        password_matched = (hashed_pwd == password)

    if password_matched:
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return jsonify({"message": "Login successful", "token": password}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route('/api/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/profile/step', methods=['POST'])
def profile_step():
    data = request.json or {}
    profile_id = data.get('profile_id')
    email = data.get('email')
    step = data.get('step', 'unknown')
    step_data = data.get('data', {})

    try:
        if profile_id:
            users_col.update_one(
                {"_id": ObjectId(profile_id)},
                {"$set": {f"profile.{step}": step_data}},
                upsert=True
            )
            ret_id = str(profile_id)
        elif email:
            user = users_col.find_one_and_update(
                {"email": email},
                {"$set": {f"profile.{step}": step_data}, "$setOnInsert": {"email": email}},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            ret_id = str(user["_id"])
        else:
            res = users_col.insert_one({
                "created_at": datetime.utcnow(),
                "profile": {
                    step: step_data
                }
            })
            ret_id = str(res.inserted_id)

        return jsonify({"profile_id": ret_id, "status": "updated"}), 200
    except Exception as e:
        app.logger.error(f"Error in profile_step: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 7. Admin API Routes
@app.route('/api/admin/dashboard-stats', methods=['GET'])
@admin_required
def dashboard_stats():
    total = engagement_col.count_documents({})
    pipeline = [{"$group": {"_id": "$interest", "count": {"$sum": 1}}}]
    categories = list(engagement_col.aggregate(pipeline))
    recent = list(engagement_col.find().sort("timestamp", -1).limit(10))
    for r in recent: r['_id'] = str(r['_id'])
    return jsonify({"total_engagements": total, "categories": categories, "recent_activity": recent})

@app.route('/api/admin/export', methods=['GET'])
@admin_required
def export_csv():
    engagements = list(engagement_col.find({}, {"_id": 0}))
    return jsonify(engagements)

@app.route('/api/admin/build_index', methods=['POST'])
@admin_required
def admin_build_index():
    try:
        count, faiss_used = build_vector_index()
        return jsonify({
            "message": "Index built successfully",
            "records_processed": count,
            "faiss_used": faiss_used
        }), 200
    except Exception as e:
        app.logger.error(f"Error in admin_build_index: {str(e)}")
        return jsonify({"error": str(e)}), 500


# --- Services CRUD ---
@app.route('/api/admin/services', methods=['GET', 'POST'])
@admin_required
def admin_services():
    if request.method == 'GET':
        services = list(services_col.find({}))
        for s in services:
            s['_id'] = str(s['_id'])
        return jsonify(services), 200
    elif request.method == 'POST':
        payload = request.json or {}
        srv_id = payload.get('id')
        if not srv_id:
            return jsonify({"error": "Missing required 'id' field"}), 400
        services_col.update_one({"id": srv_id}, {"$set": payload}, upsert=True)
        return jsonify({"status": "upserted"}), 200

@app.route('/api/admin/services/<service_id>', methods=['DELETE'])
@admin_required
def admin_delete_service(service_id):
    services_col.delete_one({"id": service_id})
    return jsonify({"status": "deleted"}), 200


# --- Categories CRUD ---
@app.route('/api/admin/categories', methods=['GET', 'POST', 'DELETE'])
@admin_required
def admin_categories():
    if request.method == 'GET':
        categories = list(categories_col.find({}))
        for c in categories:
            c['_id'] = str(c['_id'])
        return jsonify(categories), 200
    elif request.method == 'POST':
        payload = request.json or {}
        cat_id = payload.get('id')
        if not cat_id:
            return jsonify({"error": "Missing required 'id' field"}), 400
        categories_col.update_one({"id": cat_id}, {"$set": payload}, upsert=True)
        return jsonify({"status": "upserted"}), 200
    elif request.method == 'DELETE':
        cat_id = request.args.get('id')
        if not cat_id:
            return jsonify({"error": "Missing 'id' query parameter"}), 400
        categories_col.delete_one({"id": cat_id})
        return jsonify({"status": "deleted"}), 200

@app.route('/api/admin/categories/<category_id>', methods=['DELETE'])
@admin_required
def admin_delete_category_path(category_id):
    categories_col.delete_one({"id": category_id})
    return jsonify({"status": "deleted"}), 200


# --- Officers CRUD ---
@app.route('/api/admin/officers', methods=['GET', 'POST', 'DELETE'])
@admin_required
def admin_officers():
    if request.method == 'GET':
        officers = list(officers_col.find({}))
        for o in officers:
            o['_id'] = str(o['_id'])
        return jsonify(officers), 200
    elif request.method == 'POST':
        payload = request.json or {}
        off_id = payload.get('id')
        if not off_id:
            return jsonify({"error": "Missing required 'id' field"}), 400
        officers_col.update_one({"id": off_id}, {"$set": payload}, upsert=True)
        return jsonify({"status": "upserted"}), 200
    elif request.method == 'DELETE':
        off_id = request.args.get('id')
        if not off_id:
            return jsonify({"error": "Missing 'id' query parameter"}), 400
        officers_col.delete_one({"id": off_id})
        return jsonify({"status": "deleted"}), 200

@app.route('/api/admin/officers/<officer_id>', methods=['DELETE'])
@admin_required
def admin_delete_officer_path(officer_id):
    officers_col.delete_one({"id": officer_id})
    return jsonify({"status": "deleted"}), 200


# --- Ads CRUD ---
@app.route('/api/admin/ads', methods=['GET', 'POST', 'DELETE'])
@admin_required
def admin_ads():
    if request.method == 'GET':
        ads = list(ads_col.find({}))
        for a in ads:
            a['_id'] = str(a['_id'])
        return jsonify(ads), 200
    elif request.method == 'POST':
        payload = request.json or {}
        ad_id = payload.get('id')
        if not ad_id:
            return jsonify({"error": "Missing required 'id' field"}), 400
        ads_col.update_one({"id": ad_id}, {"$set": payload}, upsert=True)
        return jsonify({"status": "upserted"}), 200
    elif request.method == 'DELETE':
        ad_id = request.args.get('id')
        if not ad_id:
            return jsonify({"error": "Missing 'id' query parameter"}), 400
        ads_col.delete_one({"id": ad_id})
        return jsonify({"status": "deleted"}), 200

@app.route('/api/admin/ads/<ad_id>', methods=['DELETE'])
@admin_required
def admin_delete_ad_path(ad_id):
    ads_col.delete_one({"id": ad_id})
    return jsonify({"status": "deleted"}), 200


@app.route('/api/admin/insights', methods=['GET'])
@admin_required
def admin_insights():
    try:
        age_groups = {
            "<18": 0,
            "18-25": 0,
            "26-40": 0,
            "41-60": 0,
            "60+": 0
        }
        
        engagements = list(engagement_col.find({}))
        
        jobs_map = {}
        services_map = {}
        questions_map = {}
        desires_map = {}
        
        for eng in engagements:
            raw_age = eng.get('age')
            if raw_age is not None:
                try:
                    age = int(raw_age)
                    if age < 18:
                        age_groups["<18"] += 1
                    elif 18 <= age <= 25:
                        age_groups["18-25"] += 1
                    elif 26 <= age <= 40:
                        age_groups["26-40"] += 1
                    elif 41 <= age <= 60:
                        age_groups["41-60"] += 1
                    else:
                        age_groups["60+"] += 1
                except (ValueError, TypeError):
                    pass
            
            job = eng.get('job')
            if job:
                jobs_map[job] = jobs_map.get(job, 0) + 1
                
            service = eng.get('service')
            if service:
                services_map[service] = services_map.get(service, 0) + 1
                
            question = eng.get('question_clicked') or eng.get('question')
            if question:
                questions_map[question] = questions_map.get(question, 0) + 1
                
            desires = eng.get('desires')
            if isinstance(desires, list):
                for d in desires:
                    if d:
                        desires_map[d] = desires_map.get(d, 0) + 1
            elif isinstance(desires, str):
                if desires:
                    desires_map[desires] = desires_map.get(desires, 0) + 1

        pipeline = [
            {
                "$match": {
                    "user_id": {"$exists": True, "$ne": None},
                    "question_clicked": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": {
                        "user_id": "$user_id",
                        "question_clicked": "$question_clicked"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "count": {"$gte": 2}
                }
            },
            {
                "$project": {
                    "user_id": "$_id.user_id",
                    "question_clicked": "$_id.question_clicked",
                    "count": 1,
                    "_id": 0
                }
            }
        ]
        premium_suggestions = list(engagement_col.aggregate(pipeline))
        
        return jsonify({
            "age_groups": age_groups,
            "jobs": jobs_map,
            "services": services_map,
            "questions": questions_map,
            "desires": desires_map,
            "premium_suggestions": premium_suggestions
        }), 200
    except Exception as e:
        app.logger.error(f"Error in admin_insights: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/export_csv', methods=['GET'])
@admin_required
def admin_export_csv():
    try:
        records = list(engagement_col.find({}))
        
        si = io.StringIO()
        writer = csv.writer(si)
        
        writer.writerow(["user_id", "age", "job", "desires", "question_clicked", "service", "ad", "timestamp"])
        
        for r in records:
            user_id = r.get("user_id", "")
            age = r.get("age", "")
            job = r.get("job", "")
            
            raw_desires = r.get("desires", "")
            if isinstance(raw_desires, list):
                desires = ", ".join(str(d) for d in raw_desires)
            else:
                desires = str(raw_desires)
                
            question_clicked = r.get("question_clicked") or r.get("question") or ""
            service = r.get("service", "")
            ad = r.get("ad", "")
            
            ts = r.get("timestamp")
            if isinstance(ts, datetime):
                timestamp_str = ts.isoformat()
            elif ts:
                timestamp_str = str(ts)
            else:
                timestamp_str = ""
                
            writer.writerow([user_id, age, job, desires, question_clicked, service, ad, timestamp_str])
        
        output = si.getvalue()
        
        from flask import Response
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=engagements.csv"}
        )
    except Exception as e:
        app.logger.error(f"Error in admin_export_csv: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 8. Public API Routes
@app.route('/api/services', methods=['GET'])
def get_services():
    return jsonify(list(services_col.find({}, {"_id": 0})))

@app.route('/api/engagement', methods=['POST'])
def save_engagement():
    data = request.json
    engagement_col.insert_one(data)
    return jsonify({"message": "Success"}), 201

# AI Chat Removed

@app.route('/api/ai/search', methods=['POST'])
def ai_search():
    data = request.json or {}
    query = data.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400

    top_k = int(data.get('top_k', 5))
    try:
        hits = search_vectors(query, top_k=top_k)
        chunks = []
        source_metadata = []
        for hit in hits:
            meta = hit["metadata"]
            chunk = meta.get("content", "")
            if chunk:
                chunks.append(chunk)
            source_metadata.append(meta)

        answer_str = "\n\n---\n\n".join(chunks)
        return jsonify({
            "query": query,
            "answer": answer_str,
            "source_metadata": source_metadata
        }), 200
    except Exception as e:
        app.logger.error(f"Error in ai_search: {str(e)}")
        return jsonify({"error": str(e)}), 500

# AI Chat Implementation
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json or {}
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
        
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Use gemini-flash-latest as a stable alias
        model_name = 'gemini-flash-latest'
        
        # Retry logic for 429 errors
        import time
        for attempt in range(2):
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction="You are the official Sri Lanka Citizen Assistant. Answer questions based on the provided ministry data. Be polite and concise. Always prefer the data provided in your training if it matches Sri Lankan government services."
                )
                response = model.generate_content(prompt)
                return jsonify({"response": response.text.strip()})
            except Exception as e:
                if "429" in str(e) and attempt == 0:
                    time.sleep(2) # Wait and retry once
                    continue
                logging.warning(f"AI Attempt {attempt+1} failed: {str(e)}")
                return local_ai_fallback(prompt)

    except Exception as e:
        logging.error(f"AI CHAT CRITICAL ERROR: {str(e)}")
        return local_ai_fallback(prompt)

def local_ai_fallback(prompt):
    """Fallback logic when Gemini API is unavailable"""
    prompt_lower = prompt.lower()
    all_services = list(services_col.find({}))
    
    # 1. Smarter Keyword Search
    best_match = None
    max_matches = 0
    
    keywords = prompt_lower.split()
    for m in all_services:
        matches = 0
        m_name = m['name']['en'].lower()
        if any(word in m_name for word in keywords if len(word) > 3):
            matches += 2
            
        for s in m.get('subservices', []):
            s_name = s['name']['en'].lower()
            if any(word in s_name for word in keywords if len(word) > 3):
                matches += 1
                
            for q in s.get('questions', []):
                q_text = q['q']['en'].lower()
                if any(word in q_text for word in keywords if len(word) > 4):
                    return jsonify({"response": f"[Instant Answer] {q['answer']['en']} (Source: {m['name']['en']})"})

        if matches > max_matches:
            max_matches = matches
            best_match = m

    if best_match:
        return jsonify({
            "response": f"I've found information related to {best_match['name']['en']}. You can contact them at {best_match['contact']['phone']} or visit {best_match['links'][0]['url']} for official services."
        })
            
    return jsonify({
        "response": "I'm currently receiving many requests. While my AI is cooling down, please use keywords like 'passport', 'license', 'health', or 'tax' so I can find local answers for you!"
    })

if __name__ == '__main__':
    # Startup check for default admin
    if admins_col.count_documents({}) == 0:
        admin_user = "admin"
        admin_pwd = os.getenv('ADMIN_PWD', 'admin123')
        hashed = bcrypt.hashpw(admin_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admins_col.update_one(
            {"username": admin_user},
            {"$set": {"password": hashed, "role": "superadmin"}},
            upsert=True
        )
        print("Default administrator account generated via startup check.")

    port = int(os.getenv('PORT', 3000))
    # Disable reloader on Windows to prevent [WinError 10038]
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
