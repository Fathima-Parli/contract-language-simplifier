# Contract Language Simplifier
AI-powered tool to simplify complex legal documents

## 🚀 Milestone 1 - User Registration System

**Completed by:** Monika S 
**Date:** February 12, 2026

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- Flask 3.0.0
- PyMongo 4.6.1
- bcrypt 4.1.2
- Flask-CORS 4.0.0

**Database:**
- MongoDB 8.2.4

**Frontend:**
- HTML5, CSS3, JavaScript

---

## ✨ Features Completed

✅ User registration with email/password  
✅ Password hashing with bcrypt  
✅ MongoDB integration  
✅ Email & phone validation  
✅ Real-time form validation  
✅ Responsive UI design  
✅ RESTful API endpoints  

---

## 📁 Project Structure
```
contract-language-simplifier/
├── app.py                  # Main Flask application
├── models.py              # User model
├── requirements.txt       # Dependencies
├── .env                   # Configuration
├── config/
│   └── database.py       # MongoDB connection
├── templates/
│   └── register.html     # Registration page
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── register.js   # Validation
```

---

## 🚀 Setup Instructions for Team

### Prerequisites
- Python 3.8 or higher
- MongoDB 8.0 or higher
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/Fathima-Parli/contract-language-simplifier
cd contract-language-simplifier
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install flask flask-cors pymongo python-dotenv bcrypt email-validator
```

### Step 4: Install & Start MongoDB

**Download:** https://www.mongodb.com/try/download/community

**Start MongoDB (Windows - as Administrator):**
```bash
net start MongoDB
```

**Mac:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

### Step 5: Run Application
```bash
python app.py
```

Expected output:
```
✓ Successfully connected to MongoDB database: contract_simplifier
 * Running on http://127.0.0.1:5000
```

### Step 6: Open in Browser
```
http://localhost:5000
```

---

## 🧪 Testing

**Test Registration:**
- Name: John Doe
- Email: test@example.com
- Phone: 9876543210
- Password: test123456

**Verify in MongoDB Compass:**
1. Connect to `mongodb://localhost:27017`
2. Database: `contract_simplifier`
3. Collection: `users`

---

## 📋 API Endpoints

### POST /api/register
Register a new user

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "password": "test123"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Email already registered"
}
```

### GET /api/health
Check server status

**Response:**
```json
{
  "status": "running",
  "database": "connected"
}
```

---

## 🔒 Security Features

✅ Password hashing with bcrypt (salt rounds: 12)  
✅ Input validation (client & server side)  
✅ Unique email constraint  
✅ SQL injection prevention (NoSQL)  
✅ XSS protection  

---

## 🐛 Troubleshooting

**MongoDB connection error:**
```bash
# Windows (as Administrator)
net start MongoDB

# Check status
sc query MongoDB
```

**Port 5000 already in use:**
Change port in `app.py` (line 67):
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Module not found error:**
```bash
pip install -r requirements.txt --upgrade
```

---

**Good luck team! Let's complete Milestone 1! 🚀**
