from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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


@app.route('/login')
def login():
    """Render the login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    if not user_model:
        return jsonify({
            "success": False,
            "message": "Database connection error"
        }), 500
    
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400
            
        user = user_model.get_user_by_email(email)
        
        if not user or not user_model.verify_password(password, user['password']):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
            
        # Login successful
        session['user_id'] = str(user['_id'])
        session['name'] = user['name']
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "redirect": "/dashboard"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', name=session.get('name'))

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)