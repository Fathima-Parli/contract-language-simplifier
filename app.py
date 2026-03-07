# ... imports 
print("APP STARTED")

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from config.database import db_instance
from models import User, Document  # Modified import
import os
import time 
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from nlp.preprocessing import preprocess_pipeline
from nlp.readability import calculate_readability
from nlp.model import simplify_text, summarize_text

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure Uploads - Updated for Task 6
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max limit (increased for large docs)
ALLOWED_EXTENSIONS = {'txt'}
MAX_DOCUMENT_LENGTH = 100000  # Maximum characters per document (approx 10 pages)

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Enable CORS
CORS(app)

# Connect to MongoDB
db = db_instance.connect()

# Initialize Models
user_model = User(db) if db is not None else None
document_model = Document(db) if db is not None else None

@app.route('/')
def index():
    """Render the registration page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
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
            # Redirect to login instead of auto-login
            return jsonify({
                "success": True,
                "message": "Registration successful! Please login."
            }), 201
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
    db_status = "connected" if db is not None else "disconnected"
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
    
    # Fetch user documents
    documents = []
    if document_model:
        documents = document_model.get_user_documents(session['user_id'])

    return render_template('dashboard.html', name=session.get('name'), documents=documents)

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Handle document upload or text input"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if not document_model:
        return jsonify({"success": False, "message": "Database error"}), 500

    try:
        user_id = session['user_id']
        title = request.form.get('title', 'Untitled Document')
        doc_type = request.form.get('type', 'text') # text or file
        
        content = ""
        original_filename = None
        
        if doc_type == 'file':
            if 'file' not in request.files:
                return jsonify({"success": False, "message": "No file part"}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"success": False, "message": "No selected file"}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                original_filename = filename
                
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{user_id}_{filename}")
                file.save(filepath)
                
                # Read content for simplification (assuming txt for now)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                 return jsonify({"success": False, "message": "Invalid file type. Only .txt allowed."}), 400

        else: # text input
             content = request.form.get('content', '')
             if not content.strip():
                 return jsonify({"success": False, "message": "Content cannot be empty"}), 400

        # Save to DB
        result = document_model.create_document(user_id, title, content, doc_type, original_filename)
        
        if result['success']:
             return jsonify({
                "success": True, 
                "message": "Document uploaded successfully",
                "document_id": result['document_id']
            }), 201
        else:
             return jsonify(result), 400

    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text for readability"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"success": False, "message": "No text provided"}), 400
            
        # Preprocess
        preprocessed = preprocess_pipeline(text)
        
        # Calculate readability
        readability = calculate_readability(text)
        
        # Word complexity (imported dynamically to avoid circular issues if any, though likely fine)
        from nlp.readability import analyze_word_complexity
        complexity_map = analyze_word_complexity(text)
        
        return jsonify({
            "success": True,
            "stats": preprocessed,
            "readability": readability,
            "complexity_map": complexity_map
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Analysis error: {str(e)}"}), 500


@app.route('/document/<doc_id>')
def view_document(doc_id):
    """View a specific document"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not document_model:
        return "Database error", 500

    doc = document_model.get_document_by_id(doc_id)
    
    if not doc:
        return "Document not found", 404
        
    # Ensure user owns the document
    if str(doc['user_id']) != session['user_id']:
        return "Unauthorized", 403
        
    return render_template('view_document.html', doc=doc)

@app.route('/simplify/<doc_id>', methods=['POST'])
def simplify_document(doc_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if not document_model:
        return jsonify({"success": False, "message": "Database error"}), 500

    doc = document_model.get_document_by_id(doc_id)
    if not doc or str(doc['user_id']) != session['user_id']:
        return jsonify({"success": False, "message": "Document not found or unauthorized"}), 404
        
    try:
        data = request.get_json(silent=True) or {}
        level = int(data.get('level', 70))
        simplification_mode = data.get('simplification_mode', 'intermediate')  # NEW: Get mode

        # Validate simplification mode
        if simplification_mode not in ['basic', 'intermediate', 'advanced']:
            simplification_mode = 'intermediate'  # Default to intermediate if invalid
        
        content = doc.get("content", "")
        
        # Task 6: Check document size
        if len(content) > MAX_DOCUMENT_LENGTH:
            return jsonify({
                "success": False, 
                "message": f"Document too large. Maximum {MAX_DOCUMENT_LENGTH} characters allowed."
            }), 400
        
        # Task 6: Check if content is empty
        if not content.strip():
            return jsonify({
                "success": False,
                "message": "Document content is empty"
            }), 400
        
        # Track processing time
        start_time = time.time()
        
        # Task 6: Simplify with chunking support for large docs
        try:
            simplified = simplify_text(content, level,simplification_mode)
        except Exception as e:
            print(f"Error during simplification: {e}")
            return jsonify({
                "success": False,
                "message": f"Simplification failed: {str(e)}"
            }), 500
        
        processing_time = round(time.time() - start_time, 2)
        
        # Calculate readability for both original and simplified
        try:
            original_readability = calculate_readability(content)
            simplified_readability = calculate_readability(simplified)
        except Exception as e:
            print(f"Error calculating readability: {e}")
            # Use default values if readability calculation fails
            original_readability = {'flesch_kincaid_grade': 0}
            simplified_readability = {'flesch_kincaid_grade': 0}
        
        # Calculate metrics
        original_grade = round(original_readability['flesch_kincaid_grade'], 1)
        simplified_grade = round(simplified_readability['flesch_kincaid_grade'], 1)
        grade_reduction = round(original_grade - simplified_grade, 1)
        
        original_words = len(content.split())
        simplified_words = len(simplified.split())
        
        # Save to DB
        document_model.update_document_simplified(doc_id, simplified)
        
        # Return with metrics
        return jsonify({
            "success": True, 
            "simplified_content": simplified,
            "simplification_mode": simplification_mode,  # NEW: Return the mode used
            "metrics": {
                "processing_time": processing_time,
                "original_grade": original_grade,
                "simplified_grade": simplified_grade,
                "reduction": grade_reduction,
                "original_words": original_words,
                "simplified_words": simplified_words
            }
        })
    except Exception as e:
        print(f"Unexpected error in simplify_document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/summarize/<doc_id>', methods=['POST'])
def summarize_document(doc_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    if not document_model:
        return jsonify({"success": False, "message": "Database error"}), 500

    doc = document_model.get_document_by_id(doc_id)
    if not doc or str(doc['user_id']) != session['user_id']:
        return jsonify({"success": False, "message": "Document not found or unauthorized"}), 404
        
    try:
        content = doc.get("content", "")
        summary = summarize_text(content)
        
        # Save to DB
        document_model.update_document_summary(doc_id, summary)
        
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)