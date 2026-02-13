# Contract Language Simplifier
AI-powered tool to simplify complex legal documents into plain English.

## 🚀 Milestone Completed - Dashboard & Document Management

**Date:** February 14, 2026

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- Flask 3.0.0
- PyMongo 4.6.1
- bcrypt 4.1.2
- Flask-CORS 4.0.0

**Database:**
- MongoDB (Local/Atlas)

**Frontend:**
- HTML5, CSS3, JavaScript
- Modern UI with 'Inter' font stack
- Responsive Design

---

## ✨ Features

### 1. User Authentication
✅ **Registration**: Secure sign-up with email, name, and phone validation.
✅ **Login**: Secure login with bcrypt password hashing.
✅ **Logout**: Secure session clearing.
✅ **Security**: Input validation and session management.

### 2. User Dashboard
✅ **Overview**: View total documents and simplified count.
✅ **Upload Interface**: 
    - Upload `.txt` files.
    - Paste text directly.
✅ **Document List**: Card-based view of all uploaded documents with status indicators.

### 3. Document Management
✅ **View Document**: Clickable cards to view full original content.
✅ **Status Tracking**: Track if a document is 'Original' or 'Simplified'.
✅ **Storage**: Documents stored in MongoDB linked to the user.

---

## 📁 Project Structure
```
contract-language-simplifier/
├── app.py                  # Main Flask application (Routes & Logic)
├── models.py              # Database Models (User, Document)
├── requirements.txt       # Dependencies
├── .env                   # Configuration (Not in Repo)
├── config/
│   └── database.py       # MongoDB connection
├── templates/
│   ├── register.html     # Registration page
│   ├── login.html        # Login page
│   ├── dashboard.html    # User Dashboard
│   └── view_document.html# Document View page
└── static/
    ├── css/
    │   └── style.css     # Professional Styling
    ├── js/
    │   ├── register.js   # Auth Validation
    │   └── login.js      # Login Logic
    └── uploads/          # Temporary file storage
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB installed and running

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

### Step 4: Configure Environment
Create a `.env` file in the root directory:
```
SECRET_KEY=your_secret_key
MONGODB_URI=mongodb://localhost:27017/contract_simplifier
```

### Step 5: Run Application
```bash
python app.py
```
Access the app at `http://localhost:8000`

---

## 📋 API Endpoints

- `POST /api/register`: Register new user
- `POST /api/login`: Authenticate user
- `POST /api/upload`: Upload document or text
- `GET /dashboard`: User dashboard
- `GET /document/<id>`: View specific document

---

## 🤝 Contribution
1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request
