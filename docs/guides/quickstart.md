# 5-Minute Developer Quickstart Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- Git

## 1. Backend Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GEMINI_API_KEY or OPENAI_API_KEY
python -m uvicorn api:app --reload --port 8000
```

## 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to interact with VectraBank.
