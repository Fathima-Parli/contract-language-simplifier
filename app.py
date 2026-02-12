from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from config.database import db_instance
from models import User
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS
CORS(app)

# Connect to MongoDB
db = db_instance.connect()

# Initialize User model
user_model = User(db) if db is not None else None

@app.route('/')
def index():
    """Render the registration page"""
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Handle user registration"""
    if not user_model:
        return jsonify({
            "success": False,
            "message": "Database connection error"
        }), 500
    
    try:
        data = request.get_json()
        
        # Extract data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        
        # Create user
        result = user_model.create_user(name, email, phone, password)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_status = "connected" if db else "disconnected"
    return jsonify({
        "status": "running",
        "database": db_status
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)