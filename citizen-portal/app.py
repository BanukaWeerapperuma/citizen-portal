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

app = Flask(__name__)
CORS(app)

# 1. Initialize Google AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# Note: gemini-1.5-flash was requested, but gemini-3-flash-preview is used based on availability
model = genai.GenerativeModel('gemini-3-flash-preview')

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
    data = request.json
    content = data.get('content') # Can be string or dict
    target_lang = data.get('target_lang') # 'si', 'ta', 'en'
    
    lang_names = {"si": "Sinhala", "ta": "Tamil", "en": "English"}
    lang_name = lang_names.get(target_lang, "English")
    
    if target_lang == 'en':
        return jsonify({"translated": content})

    prompt = f"Translate the following content into {lang_name}. If it's a list or object, translate only the values. Return only the translated content:\n\n{content}"
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"translated": response.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    return jsonify({"message": "User registered successfully"}), 201

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
    if not engagements: return jsonify({"error": "No data"}), 404
    si = io.StringIO()
    cw = csv.DictWriter(si, fieldnames=engagements[0].keys())
    cw.writeheader()
    cw.writerows(engagements)
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='engagements.csv')

# 8. Public API Routes
@app.route('/api/services', methods=['GET'])
def list_services():
    services = list(services_col.find({}, {"_id": 0}))
    return jsonify(services)

@app.route('/api/engagement', methods=['POST'])
def log_engagement():
    data = request.json
    engagement_col.insert_one(data)
    return jsonify({"message": "Success"}), 201

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.json
    prompt = data.get('prompt')
    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text, "model": model.model_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
