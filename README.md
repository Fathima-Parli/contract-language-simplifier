# Contract Language Simplifier

> **AI-powered tool that transforms complex legal documents into plain, easy-to-understand English.**

---

## 🚀 Milestone 4 Completed — Multi-level Simplification, Key Term Highlighting & Admin Dashboard

**Date:** March 7, 2026

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12+, Flask 3.0.0, Flask-CORS 4.0.0, Flask-Session 0.6.0 |
| **AI / NLP** | HuggingFace Transformers (FLAN-T5), PyTorch, SpaCy, NLTK |
| **Readability** | Textstat (Flesch-Kincaid, Gunning Fog) |
| **Database** | MongoDB (Local / Atlas) via PyMongo 4.6.1 |
| **Auth** | bcrypt 4.1.2, Flask Sessions |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Inter font |

---

## ✨ Features — All Milestones

### 🔵 Milestone 1 — User Authentication
- ✅ **Registration** — Secure signup with name, email, phone & password validation
- ✅ **Login / Logout** — bcrypt password hashing, secure session management
- ✅ **Dashboard** — View and manage all uploaded documents

---

### 🔵 Milestone 2 — NLP & Readability Analysis
- ✅ **Text Preprocessing** — Cleaning, sentence segmentation (SpaCy), tokenization (NLTK)
- ✅ **Readability Scores** — Flesch-Kincaid Grade Level & Gunning Fog Index
- ✅ **Word Complexity Heatmap** — Visual difficulty map directly on the text:
  - 🔴 Complex (3+ syllables)
  - 🟡 Medium (7+ chars)
  - 🟢 Simple vocabulary

---

### 🔵 Milestone 3 — AI Model Integration (FLAN-T5)
- ✅ **Text Simplification** — FLAN-T5 model rewrites legal text in plain English
- ✅ **Adjustable Level** — Interactive slider (1–100) dynamically maps to model prompt intensity
- ✅ **Hybrid Summarization** — AI summary with NLTK extractive fallback
- ✅ **Readability Bar Chart** — Live JS bar chart showing grade drop after simplification
- ✅ **Document Upload** — Supports `.txt` file uploads up to 50 MB

---

### 🟢 Milestone 4 — NEW: Advanced Features

#### 1. Multi-level Simplification Mode
- ✅ **Three distinct modes** selectable via large card buttons:
  - 📘 **Basic** — Minimal changes, preserves legal structure
  - 📗 **Intermediate** — Balanced (default) — replaces jargon with everyday language
  - 📕 **Advanced** — Maximum simplification, suitable for anyone
- ✅ The selected mode is sent to the backend API (`simplification_mode` field)
- ✅ A **mode badge** appears on the simplified text card after processing
- ✅ Processing metrics displayed: time, grade reduction, original/simplified word count

#### 2. Key Term Highlighting & Legal Glossary
- ✅ **80+ legal terms** detected automatically in uploaded documents
- ✅ Detected terms are **highlighted in amber** in the Original Text pane
- ✅ **Hover tooltips** show plain-English definitions instantly
- ✅ **Searchable Legal Terms Glossary** panel — collapsible, with live search filter
- ✅ Custom glossary terms (added by admin) are merged into results
- ✅ API endpoint: `POST /api/highlight_terms`

#### 3. Admin Dashboard (`/admin`)
- ✅ **Sidebar navigation** with 4 tabs:
  | Tab | What it shows |
  |---|---|
  | 📊 Overview | Stat cards (total requests, avg time, avg grade reduction, docs, users) + mode breakdown bar chart + 7-day daily activity chart |
  | 📋 Requests | Paginated table of every simplification log (date, document, mode, level, grades, time) |
  | 📝 Document Review | All documents across all users — click any row to open inline correction editor, save corrected simplified text |
  | 📚 Glossary Management | Add / delete custom legal term definitions that merge into highlighting results |
- ✅ All simplification requests are **automatically logged** to MongoDB
- ✅ Admin access: **first registered user** automatically becomes admin
- ✅ One-time setup endpoint `POST /api/setup-admin` for existing users

---

## 📁 Project Structure

```
contract-language-simplifier/
├── app.py                     # Main Flask app — all routes & logic
├── models.py                  # MongoDB models:
│                              #   User, Document, SimplificationLog, GlossaryTerm
├── requirements.txt           # All Python dependencies
├── .env                       # Environment config (not in repo)
│
├── nlp/
│   ├── model.py               # FLAN-T5 simplification & summarization
│   ├── legal_terms.py         # 80+ term glossary, highlighting & tooltip HTML   ← NEW
│   ├── readability.py         # Flesch-Kincaid & Gunning Fog scoring
│   ├── preprocessing.py       # SpaCy/NLTK text cleaning pipeline
│   └── chunking.py            # Large document chunking for FLAN-T5
│
├── templates/
│   ├── view_document.html     # Document viewer — mode cards, highlighted text,
│   │                          # glossary panel, metrics, bar chart             ← REDESIGNED
│   ├── admin.html             # Admin dashboard with 4 tabs                    ← NEW
│   ├── dashboard.html         # User dashboard
│   ├── login.html             # Login page
│   └── register.html          # Registration page
│
└── static/
    ├── css/
    │   ├── style.css          # Dashboard styles
    │   └── auth.css           # Login/Register styles
    └── js/                    # Frontend logic
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB installed and running locally (or MongoDB Atlas URI)

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
python -m spacy download en_core_web_sm
```

### Step 4: Configure Environment
Create a `.env` file in the project root:
```env
SECRET_KEY=your_secret_key_here
MONGODB_URI=mongodb://localhost:27017/contract_simplifier
```

### Step 5: Run Application
```bash
python app.py
```
Open your browser at **http://localhost:8000**

---

## 📋 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register` | Register new user |
| `POST` | `/api/login` | Authenticate user |
| `GET` | `/logout` | Clear session & logout |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a document (text or `.txt` file) |
| `GET` | `/document/<doc_id>` | View document with highlighting & tools |
| `POST` | `/simplify/<doc_id>` | Simplify text — accepts `level` (1-100) & `simplification_mode` (basic/intermediate/advanced) |
| `POST` | `/summarize/<doc_id>` | Generate hybrid AI summary |
| `POST` | `/api/analyze` | Analyze text for readability scores |
| `POST` | `/api/highlight_terms` | Detect & highlight legal terms in text |

### Admin (🔐 Admin only)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin` | Admin dashboard UI |
| `GET` | `/api/admin/stats` | Aggregated usage statistics |
| `GET` | `/api/admin/requests` | Paginated simplification request logs |
| `GET` | `/api/admin/documents` | All documents (all users) |
| `POST` | `/api/admin/document/<id>/correct` | Save admin-corrected simplified text |
| `GET` | `/api/admin/glossary` | List custom glossary terms |
| `POST` | `/api/admin/glossary` | Add custom legal term |
| `DELETE` | `/api/admin/glossary/<id>` | Delete custom term |
| `POST` | `/api/setup-admin` | One-time: grant admin to logged-in user |

---

## 🔐 Admin Access

The **first user to register** is automatically granted admin privileges.

**Already registered before admin was added?** Run this in the browser console while logged in:
```javascript
fetch('/api/setup-admin', {method:'POST'})
  .then(r=>r.json())
  .then(d=>{ alert(d.message); if(d.redirect) window.location=d.redirect; })
```

---

## 📸 UI Overview

| Screen | Description |
|---|---|
| **Document View** | Blue gradient header, User View / Admin Dashboard tabs, 3 simplification mode cards, side-by-side original & simplified text, legal term highlighting with tooltips, searchable glossary panel |
| **Admin Dashboard** | Navy sidebar, 4-tab layout, stat cards, mode breakdown & activity charts, document correction editor, glossary CRUD |

---

## 📦 Dependencies

```
flask==3.0.0
flask-cors==4.0.0
flask-session==0.6.0
pymongo==4.6.1
python-dotenv==1.0.0
bcrypt==4.1.2
email-validator==2.1.0
transformers
torch
spacy
nltk
textstat
```
