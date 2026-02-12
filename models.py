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
    
    def create_user(self, name, email, phone, password):
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
                "is_active": True
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