# ... imports 
print("APP STARTED")

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from config.database import db_instance
from models import User, Document, SimplificationLog, GlossaryTerm  # Updated import
import os
import time 
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from nlp.preprocessing import preprocess_pipeline
from nlp.readability import calculate_readability
from nlp.model import simplify_text, summarize_text
from flask import jsonify
from bson.objectid import ObjectId
# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
import uuid

@app.before_request
def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
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
log_model = SimplificationLog(db) if db is not None else None
glossary_model = GlossaryTerm(db) if db is not None else None

# ─────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────
def is_admin():
    """Check if current user is admin — checks DB directly to handle
    users registered before the is_admin field was added."""
    if 'user_id' not in session:
        return False
    # Fast path: session already says admin
    if str(session.get('is_admin')).lower() == 'true':
        return True
    # Slow path: check DB (handles migration case)
    if user_model:
        user = user_model.get_user_by_id(session['user_id'])
        if user and str(user.get('is_admin')).lower() == 'true':
            session['is_admin'] = True   # update session so fast path works next time
            return True
    return False


@app.route('/api/setup-admin', methods=['POST'])
def setup_admin():
    """One-time setup: grant admin to the logged-in user if NO admin exists yet.
    Also promotes the logged-in user if they are the only user in the system."""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Must be logged in"}), 401
    if not user_model:
        return jsonify({"success": False, "message": "DB not connected"}), 500

    # Allow if there is currently no admin in the DB
    existing_admin = user_model.collection.find_one({"is_admin": True})
    total_users = user_model.collection.count_documents({})

    if existing_admin and total_users > 1:
        return jsonify({"success": False, "message": "Admin already assigned"}), 403

    # Promote current user
    from bson.objectid import ObjectId
    user_model.collection.update_one(
        {"_id": ObjectId(session['user_id'])},
        {"$set": {"is_admin": True}}
    )
    session['is_admin'] = True
    return jsonify({"success": True, "message": "Admin access granted! Redirecting…", "redirect": "/admin"})

# ─────────────────────────────────────────────
#  Public routes
# ─────────────────────────────────────────────
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

        # First registered user becomes admin
        is_first_user = user_model.collection.count_documents({}) == 0
        
        # Create user
        result = user_model.create_user(name, email, phone, password, is_admin=is_first_user)
        
        if result['success']:
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
        session['is_admin'] = str(user.get('is_admin', False)).lower() == 'true'
        
        redirect_url = "/admin" if session['is_admin'] else "/dashboard"
        return jsonify({
            "success": True,
            "message": "Login successful",
            "redirect": redirect_url,
            "is_admin": session['is_admin']
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

    return render_template('dashboard.html', name=session.get('name'), documents=documents, is_admin=session.get('is_admin', False))

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


@app.route('/api/highlight_terms', methods=['POST'])
def highlight_terms():
    """Find and return legal terms present in the given text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({"success": False, "message": "No text provided"}), 400

        from nlp.legal_terms import find_legal_terms, highlight_text_html
        terms = find_legal_terms(text)
        highlighted_html = highlight_text_html(text)

        # Also merge in custom glossary terms from DB
        custom_terms = []
        if glossary_model:
            custom_terms = glossary_model.get_all_terms()

        return jsonify({
            "success": True,
            "terms": terms,
            "highlighted_html": highlighted_html,
            "custom_glossary": custom_terms
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Highlight error: {str(e)}"}), 500


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
        
    return render_template('view_document.html', doc=doc, is_admin=session.get('is_admin', False))

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
        simplification_mode = data.get('simplification_mode', 'intermediate')

        # Validate simplification mode
        if simplification_mode not in ['basic', 'intermediate', 'advanced']:
            simplification_mode = 'intermediate'
        
        content = doc.get("content", "")
        
        if len(content) > MAX_DOCUMENT_LENGTH:
            return jsonify({
                "success": False, 
                "message": f"Document too large. Maximum {MAX_DOCUMENT_LENGTH} characters allowed."
            }), 400
        
        if not content.strip():
            return jsonify({
                "success": False,
                "message": "Document content is empty"
            }), 400
        
        # Track processing time
        start_time = time.time()
        
        try:
            simplified = simplify_text(content, level, simplification_mode)
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

        # Log simplification request for admin monitoring
        if log_model:
            try:
                log_model.create_log(
                    user_id=session['user_id'],
                    doc_id=doc_id,
                    doc_title=doc.get('title', 'Untitled'),
                    mode=simplification_mode,
                    level=level,
                    processing_time=processing_time,
                    original_grade=original_grade,
                    simplified_grade=simplified_grade,
                    original_words=original_words,
                    simplified_words=simplified_words
                )
            except Exception as log_err:
                print(f"Warning: Could not log simplification: {log_err}")
        
        # Return with metrics
        return jsonify({
            "success": True, 
            "simplified_content": simplified,
            "simplification_mode": simplification_mode,
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

# ─────────────────────────────────────────────
#  Admin routes
# ─────────────────────────────────────────────

@app.route('/admin')
def admin_dashboard():
    """Render the admin dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if not is_admin():
        return redirect(url_for('dashboard'))
    return render_template('admin.html', name=session.get('name'))


@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Return aggregated stats for the admin dashboard"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        stats = {}
        if log_model:
            stats = log_model.get_stats()
        if document_model:
            stats['total_documents'] = document_model.collection.count_documents({})
        if user_model:
            stats['total_users'] = user_model.collection.count_documents({})
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/requests', methods=['GET'])
def admin_requests():
    """Return recent simplification requests"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        logs = log_model.get_recent_logs(page=page, per_page=per_page) if log_model else []
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/documents', methods=['GET'])
def admin_documents():
    """Return all documents for review"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        docs = document_model.get_all_documents(page=page, per_page=per_page) if document_model else []
        return jsonify({"success": True, "documents": docs})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/document/<doc_id>/correct', methods=['POST'])
def admin_correct_document(doc_id):
    """Allow admin to save a corrected simplified text"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        data = request.get_json()
        corrected_text = data.get('corrected_text', '').strip()
        if not corrected_text:
            return jsonify({"success": False, "message": "Corrected text cannot be empty"}), 400

        if document_model:
            document_model.update_document_simplified(doc_id, corrected_text)
            # Mark as admin-corrected
            document_model.collection.update_one(
                {"_id": __import__('bson').ObjectId(doc_id)},
                {"$set": {"admin_corrected": True, "admin_corrected_by": session['user_id']}}
            )
        return jsonify({"success": True, "message": "Correction saved successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/glossary', methods=['GET'])
def admin_get_glossary():
    """Get all custom glossary terms"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        terms = glossary_model.get_all_terms() if glossary_model else []
        return jsonify({"success": True, "terms": terms})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/glossary', methods=['POST'])
def admin_add_glossary():
    """Add a custom glossary term"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        data = request.get_json()
        term = data.get('term', '').strip().lower()
        definition = data.get('definition', '').strip()
        if not term or not definition:
            return jsonify({"success": False, "message": "Term and definition are required"}), 400

        result = glossary_model.add_term(term, definition, session['user_id']) if glossary_model else {"success": False}
        return jsonify(result), 201 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/glossary/<term_id>', methods=['DELETE'])
def admin_delete_glossary(term_id):
    """Delete a custom glossary term"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        result = glossary_model.delete_term(term_id) if glossary_model else {"success": False}
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/admin/glossary/<term_id>', methods=['PUT'])
def admin_update_glossary(term_id):
    """Update a custom glossary term"""
    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:
        data = request.get_json()
        term = data.get('term', '').strip().lower()
        definition = data.get('definition', '').strip()
        if not term or not definition:
            return jsonify({"success": False, "message": "Term and definition required"}), 400

        result = glossary_model.update_term(term_id, term, definition) if glossary_model else {"success": False}
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
from bson.objectid import ObjectId

@app.route("/api/admin/users")
def get_all_users():

    users = list(db_instance.db.users.find())

    user_list = []

    for user in users:

        user_id = str(user["_id"])

        # Count requests
        req_count = db_instance.db.simplification_logs.count_documents({
            "user_id": user_id
        })

        # Count documents (FIX)
        doc_count = db_instance.db.documents.count_documents({
            "user_id": ObjectId(user_id)
        })

        user_list.append({
            "_id": user_id,
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "created_at": user.get("created_at", ""),
            "requests": req_count,
            "documents": doc_count
        })

    return jsonify({
        "success": True,
        "users": user_list
    })
@app.route("/api/admin/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):

    try:

        # Delete user
        db_instance.db.users.delete_one({
            "_id": ObjectId(user_id)
        })

        # Delete user's documents
        db_instance.db.documents.delete_many({
            "user_id": user_id
        })

        # Delete user's simplification logs
        db_instance.db.simplification_logs.delete_many({
            "user_id": user_id
        })

        return jsonify({
            "success": True,
            "message": "User deleted successfully"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })
from bson.objectid import ObjectId

@app.route("/api/admin/users/<user_id>/activity")
def get_user_activity(user_id):

    if 'user_id' not in session or not is_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    try:

        documents = list(db_instance.db.documents.find({
            "user_id": ObjectId(user_id)
        }))

        document_list = []

        for d in documents:
            document_list.append({
                "title": d.get("title", ""),
                "type": d.get("type", ""),
                "date": str(d.get("created_at", ""))
            })


        # Get simplification requests by the user
        logs = list(db_instance.db.simplification_logs.find({
            "user_id": user_id
        }))

        request_list = []

        for r in logs:
            request_list.append({
                "document": r.get("document_name", ""),
                "mode": r.get("mode", ""),
                "level": r.get("level", ""),
                "original_grade": r.get("original_grade", ""),
                "simplified_grade": r.get("simplified_grade", ""),
                "time": r.get("processing_time", "")
            })


        return jsonify({
            "success": True,
            "documents": document_list,
            "requests": request_list
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)