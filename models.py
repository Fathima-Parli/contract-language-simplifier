from datetime import datetime
import bcrypt
import re
from bson.objectid import ObjectId

class User:
    def __init__(self, db):
        self.collection = db['users']
        # Create unique index on email
        self.collection.create_index("email", unique=True)
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        """Validate phone number (10 digits)"""
        pattern = r'^[0-9]{10}$'
        return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    def create_user(self, name, email, phone, password, is_admin=False):
        """Create a new user"""
        try:
            # Validate inputs
            if not name or len(name.strip()) < 2:
                return {"success": False, "message": "Name must be at least 2 characters long"}
            
            if not self.validate_email(email):
                return {"success": False, "message": "Invalid email format"}
            
            if not self.validate_phone(phone):
                return {"success": False, "message": "Phone number must be 10 digits"}
            
            if not password or len(password) < 6:
                return {"success": False, "message": "Password must be at least 6 characters long"}
            
            # Check if user already exists
            if self.collection.find_one({"email": email.lower()}):
                return {"success": False, "message": "Email already registered"}
            
            # Create user document
            user_doc = {
                "name": name.strip(),
                "email": email.lower(),
                "phone": phone.replace('-', '').replace(' ', ''),
                "password": self.hash_password(password),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,
                "is_admin": is_admin
            }
            
            # Insert into database
            result = self.collection.insert_one(user_doc)
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user_id": str(result.inserted_id)
            }
        
        except Exception as e:
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def get_user_by_email(self, email):
        """Retrieve user by email"""
        return self.collection.find_one({"email": email.lower()})
    
    def get_user_by_id(self, user_id):
        """Retrieve user by ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None

class Document:
    def __init__(self, db):
        self.collection = db['documents']
        # Create index on user_id for faster queries
        self.collection.create_index("user_id")
    
    def create_document(self, user_id, title, content, doc_type='text', original_filename=None):
        """Create a new document entry"""
        try:
            doc = {
                "user_id": ObjectId(user_id),
                "title": title,
                "content": content,
                "type": doc_type,  # 'text' or 'file'
                "original_filename": original_filename,
                "simplified_content": None,
                "summary": None,
                "created_at": datetime.utcnow(),
                "status": "original",  # original, simplified
                "admin_corrected": False
            }
            
            result = self.collection.insert_one(doc)
            
            return {
                "success": True,
                "message": "Document saved successfully",
                "document_id": str(result.inserted_id)
            }
        except Exception as e:
            return {"success": False, "message": f"Error saving document: {str(e)}"}
    
    def get_user_documents(self, user_id):
        """Get all documents for a specific user"""
        try:
            documents = list(self.collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
            for doc in documents:
                doc['_id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
            return documents
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []

    def get_document_by_id(self, doc_id):
        """Get a specific document by ID"""
        try:
            doc = self.collection.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
            return doc
        except:
            return None

    def get_all_documents(self, page=1, per_page=20):
        """Get all documents (admin use) with pagination"""
        try:
            skip = (page - 1) * per_page
            documents = list(
                self.collection.find({})
                .sort("created_at", -1)
                .skip(skip)
                .limit(per_page)
            )
            for doc in documents:
                doc['_id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
                # Truncate content for listing
                if doc.get('content'):
                    doc['content_preview'] = doc['content'][:200] + ('...' if len(doc['content']) > 200 else '')
                else:
                    doc['content_preview'] = ''
                if doc.get('simplified_content'):
                    doc['simplified_preview'] = doc['simplified_content'][:200] + (
                        '...' if len(doc['simplified_content']) > 200 else '')
                else:
                    doc['simplified_preview'] = ''
            total = self.collection.count_documents({})
            return {"items": documents, "total": total, "page": page, "per_page": per_page}
        except Exception as e:
            print(f"Error fetching all documents: {e}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page}

    def update_document_simplified(self, doc_id, simplified_content):
        """Update document with simplified content"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {
                    "simplified_content": simplified_content,
                    "status": "simplified"
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating simplified content: {e}")
            return False

    def update_document_summary(self, doc_id, summary_content):
        """Update document with summary"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {
                    "summary": summary_content
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating summary: {e}")
            return False


class SimplificationLog:
    """Tracks every simplification request for admin monitoring."""

    def __init__(self, db):
        self.collection = db['simplification_logs']
        self.collection.create_index("created_at")
        self.collection.create_index("user_id")

    def create_log(self, user_id, doc_id, doc_title, mode, level,
                   processing_time, original_grade, simplified_grade,
                   original_words, simplified_words):
        """Insert a new log entry."""
        try:
            log = {
                "user_id": str(user_id),
                "doc_id": str(doc_id),
                "doc_title": doc_title,
                "mode": mode,
                "level": level,
                "processing_time": processing_time,
                "original_grade": original_grade,
                "simplified_grade": simplified_grade,
                "grade_reduction": round(original_grade - simplified_grade, 1),
                "original_words": original_words,
                "simplified_words": simplified_words,
                "created_at": datetime.utcnow()
            }
            result = self.collection.insert_one(log)
            return {"success": True, "log_id": str(result.inserted_id)}
        except Exception as e:
            print(f"Error creating log: {e}")
            return {"success": False}

    def get_recent_logs(self, page=1, per_page=20):
        """Fetch paginated recent logs."""
        try:
            skip = (page - 1) * per_page
            logs = list(
                self.collection.find({})
                .sort("created_at", -1)
                .skip(skip)
                .limit(per_page)
            )
            for log in logs:
                log['_id'] = str(log['_id'])
                if log.get('created_at'):
                    log['created_at'] = log['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            total = self.collection.count_documents({})
            return {"items": logs, "total": total, "page": page, "per_page": per_page}
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page}

    def get_stats(self):
        """Return aggregated statistics."""
        try:
            total = self.collection.count_documents({})
            if total == 0:
                return {
                    "total_requests": 0,
                    "avg_processing_time": 0,
                    "avg_grade_reduction": 0,
                    "requests_by_mode": {"basic": 0, "intermediate": 0, "advanced": 0},
                    "recent_activity": []
                }

            # Aggregation pipeline for stats
            agg_result = list(self.collection.aggregate([
                {"$group": {
                    "_id": None,
                    "avg_time": {"$avg": "$processing_time"},
                    "avg_reduction": {"$avg": "$grade_reduction"},
                    "total": {"$sum": 1}
                }}
            ]))

            # Requests by mode
            mode_agg = list(self.collection.aggregate([
                {"$group": {"_id": "$mode", "count": {"$sum": 1}}}
            ]))
            mode_counts = {"basic": 0, "intermediate": 0, "advanced": 0}
            for item in mode_agg:
                if item['_id'] in mode_counts:
                    mode_counts[item['_id']] = item['count']

            # Recent activity (last 7 days, by day)
            from datetime import timedelta
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            daily_agg = list(self.collection.aggregate([
                {"$match": {"created_at": {"$gte": seven_days_ago}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1},
                    "avg_time": {"$avg": "$processing_time"}
                }},
                {"$sort": {"_id": 1}}
            ]))

            stats = agg_result[0] if agg_result else {}
            return {
                "total_requests": total,
                "avg_processing_time": round(stats.get("avg_time", 0), 2),
                "avg_grade_reduction": round(stats.get("avg_reduction", 0), 2),
                "requests_by_mode": mode_counts,
                "recent_activity": [{"date": d["_id"], "count": d["count"], "avg_time": round(d["avg_time"], 2)} for d in daily_agg]
            }
        except Exception as e:
            print(f"Error computing stats: {e}")
            return {"total_requests": 0, "avg_processing_time": 0, "avg_grade_reduction": 0,
                    "requests_by_mode": {}, "recent_activity": []}


class GlossaryTerm:
    """Manages custom legal term definitions (admin-managed)."""

    def __init__(self, db):
        self.collection = db['glossary_terms']
        self.collection.create_index("term", unique=True)

    def get_all_terms(self):
        """Return all custom glossary terms."""
        try:
            terms = list(self.collection.find({}).sort("term", 1))
            for t in terms:
                t['_id'] = str(t['_id'])
                if t.get('created_at'):
                    t['created_at'] = t['created_at'].strftime('%Y-%m-%d %H:%M')
            return terms
        except Exception as e:
            print(f"Error fetching glossary: {e}")
            return []

    def add_term(self, term, definition, created_by):
        """Add a new custom glossary term."""
        try:
            doc = {
                "term": term.lower().strip(),
                "display_term": term.strip().title(),
                "definition": definition.strip(),
                "created_by": str(created_by),
                "created_at": datetime.utcnow()
            }
            result = self.collection.insert_one(doc)
            return {"success": True, "term_id": str(result.inserted_id)}
        except Exception as e:
            if "duplicate" in str(e).lower():
                return {"success": False, "message": "Term already exists in glossary"}
            return {"success": False, "message": str(e)}

    def delete_term(self, term_id):
        """Delete a glossary term by ID."""
        try:
            result = self.collection.delete_one({"_id": ObjectId(term_id)})
            return {"success": result.deleted_count > 0,
                    "message": "Term deleted" if result.deleted_count > 0 else "Term not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_term(self, term_id, term, definition):
        """Update an existing glossary term."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(term_id)},
                {"$set": {
                    "term": term.lower().strip(),
                    "display_term": term.strip().title(),
                    "definition": definition.strip()
                }}
            )
            return {"success": result.modified_count > 0,
                    "message": "Term updated" if result.modified_count > 0 else "Nothing changed"}
        except Exception as e:
            return {"success": False, "message": str(e)}