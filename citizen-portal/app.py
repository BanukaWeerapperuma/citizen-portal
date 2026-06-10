import os
from flask import Flask, request, jsonify, render_template, send_file
import csv
import io
from flask_cors import CORS
from pymongo import MongoClient
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
    # Force admin/admin123 for now to fix user's login issue
    admin_user = "admin"
    admin_pwd = "admin123"
    admins_col.update_one(
        {"username": admin_user},
        {"$set": {"password": admin_pwd, "role": "superadmin"}},
        upsert=True
    )
    print(f"Admin user '{admin_user}' verified/created with password '{admin_pwd}'.")

# 4b. No Translation API needed here.

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

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    admin = admins_col.find_one({"username": username, "password": password})
    if admin:
        return jsonify({"message": "Login successful", "token": password}), 200
    return jsonify({"error": "Invalid credentials"}), 401

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
    port = int(os.getenv('PORT', 3000))
    # Disable reloader on Windows to prevent [WinError 10038]
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
