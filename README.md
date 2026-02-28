# Contract Language Simplifier
AI-powered tool to simplify complex legal documents into plain English.

## 🚀 Milestone 3 Completed - AI Model Text Simplification & Summarization

**Date:** February 28, 2026

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- Flask 3.0.0
- **AI & NLP:** HuggingFace Transformers (FLAN-T5), PyTorch, NLTK, SpaCy
- **Readability:** Textstat
- PyMongo 4.6.1
- bcrypt 4.1.2
- Flask-CORS 4.0.0

**Database:**
- MongoDB (Local/Atlas)

**Frontend:**
- HTML5, CSS3, JavaScript
- Modern UI with 'Inter' font stack
- **Visualization:** Word Complexity Heatmap

---

## ✨ Features

### 1. NLP & Readability Analysis (Milestone 2)
✅ **Text Preprocessing**: Robust cleaning, sentence segmentation (SpaCy), and tokenization (NLTK).
✅ **Readability Scoring**:
    - **Flesch-Kincaid Grade Level**: Assesses educational level required to understand the text.
    - **Gunning Fog Index**: Estimates years of formal education needed.
✅ **Word Complexity Heatmap**: Visualizes difficulty levels directly on the text.
    - 🔴 **Complex**: 3+ syllables
    - 🟡 **Medium**: Long words (>7 chars)
    - 🟢 **Simple**: Standard vocabulary

### 2. AI Model Integration (Milestone 3)
✅ **FLAN-T5 Simplification**: Direct model generation scaling dynamically utilizing PyTorch & Transformers.
✅ **Adjustable Simplification Level**: User-interactive slider (1-100) dynamically mapped to token outputs and model prompts directly in the API.
✅ **Hybrid Summarization**: Model seamlessly generates document summaries, automatically falling back to an NLTK Extractive logic pipeline if text is too sparse.
✅ **Dynamic Graphing**: Live Javascript interactive graphs demonstrating readability drops in Grade Level.

### 3. User Authentication
✅ **Registration**: Secure sign-up with email, name, and phone validation.
✅ **Login**: Secure login with bcrypt password hashing.
✅ **Logout**: Secure session clearing.

### 4. User Dashboard
✅ **Analysis Interface**: Paste legal text to instantly check readability scores.
✅ **Document Management**: Upload, view, and manage legal documents.
✅ **Professional UI**: Glassmorphism design with a clean "White & Blue" theme.

---

## 📁 Project Structure
```
contract-language-simplifier/
├── app.py                 # Main Flask application (Routes & Logic)
├── models.py              # Database Models (User, Document)
├── requirements.txt       # Dependencies
├── .env                   # Configuration (Not in Repo)
├── nlp/
│   ├── preprocessing.py   # Text cleaning & tokenization
│   ├── readability.py     # Score calculation & complexity analysis
│   └── model.py           # FLAN-T5 integration for simplification & summarization
├── static/
│   ├── css/
│   │   ├── style.css      # Dashboard Styling
│   │   └── auth.css       # Login/Register Styling
│   └── js/                # Frontend Logic
└── templates/             # HTML Templates
    ├── dashboard.html     # User Dashboard
    ├── login.html         # Login Page
    ├── register.html      # Registration Page
    └── view_document.html # Document Viewer, Analysis & Slicer UI
```
├── static/
│   ├── css/
│   │   ├── style.css      # Dashboard Styling
│   │   └── auth.css       # Login/Register Styling
│   └── js/                # Frontend Logic
└── templates/             # HTML Templates
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
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
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

- `GET /document/<doc_id>`: View specific document and interface
- `POST /api/analyze`: Analyze text for readability and complexity
- `POST /api/register`: Register new user
- `POST /api/login`: Authenticate user
- `POST /api/upload`: Upload document
- `POST /simplify/<doc_id>`: Generate AI simplified text (accepts `level` payload)
- `POST /summarize/<doc_id>`: Generate hybrid AI summary
