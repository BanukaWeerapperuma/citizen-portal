import os
from flask import Flask, request, jsonify, render_template, send_file
import csv
import io
from flask_cors import CORS
from pymongo import MongoClient
import google.generativeai as genai
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import logging

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

app = Flask(__name__)
CORS(app)

@app.route('/api/ping')
def ping():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()})

# 2. Connect to MongoDB
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client.get_default_database()  # This will use 'vibex' from the URI

# Collections
admins_col = db['admins']
services_col = db['services']
engagement_col = db['engagement']
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

# 4b. Translation API using Gemini
@app.route('/api/translate', methods=['POST'])
def translate_content():
    data = request.json or {}
    content = data.get('content')
    target_lang = data.get('target_lang', 'en')
    
    if not content or target_lang == 'en':
        return jsonify({"translated": content})
        
    try:
        lang_name = "Sinhala" if target_lang == "si" else "Tamil"
        prompt = f"Translate the following text to {lang_name}. Provide ONLY the translation: {content}"
        
        # Use verified stable model
        t_model = genai.GenerativeModel('gemini-1.5-flash')
        response = t_model.generate_content(prompt)
        
        return jsonify({"translated": response.text.strip()})
    except Exception as e:
        err_msg = str(e)
        logging.error(f"Translation Error: {err_msg}")
        return jsonify({"translated": content})

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

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json or {}
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
        
    try:
        logging.info(f"AI Request: {prompt}")
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        # Using 1.5-flash which is the standard for most free-tier users
        chat_model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = f"You are the AI Assistant for the Sri Lankan Citizen Services Portal. Answer this citizen query politely: {prompt}"
        response = chat_model.generate_content(full_prompt)
        
        if response and response.text:
            return jsonify({
                "response": response.text.strip(),
                "model": "gemini-1.5-flash"
            })
        else:
            return jsonify({"error": "Empty response from AI"}), 500
            
    except Exception as e:
        err_msg = str(e)
        logging.exception("AI CHAT ERROR")
        
        if "429" in err_msg or "quota" in err_msg.lower():
            return jsonify({"error": "AI Quota Exceeded. Please try again in a few minutes or check your API billing."}), 429
            
        return jsonify({"error": f"AI Engine Error: {err_msg}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
