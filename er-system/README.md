# ER Load Balancer System

> AI-powered emergency room patient distribution using Google AI Ecosystem Stack

## Quick Start (Local)

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your project
export GOOGLE_CLOUD_PROJECT=your-gcp-project-id
export VERTEX_AI_LOCATION=us-central1

# 4. Authenticate
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 5. Seed the database (first time only)
python -m data.seed_hospitals

# 6. Start backend
uvicorn backend.main:app --reload --port 8000

# 7. Open frontend
open frontend/index.html
```

---

## Fix Firestore /hospitals Error

The most common cause is the Firestore API not being enabled:

```bash
# Enable required APIs
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com

# Re-authenticate with quota project
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

Then check your `GOOGLE_CLOUD_PROJECT` env var matches your actual project ID.

---

## Tech Stack (Hackathon Requirements)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| 🧠 Intelligence | Gemini 1.5 Flash / Pro | AI decision engine |
| 🎯 Orchestrator | Vertex AI Agent Builder | Agentic workflows |
| 🗄️ Database | Google Cloud Firestore | Real-time hospital data |
| 🚀 Deployment | Google Cloud Run | Serverless backend |
| 🔍 Context/RAG | Vertex AI Search | Grounded medical data |
| 🛠️ Dev | Google Cloud Workstations + AI Studio | Build & test |

---

## API Endpoints

```
GET  /              → Health check
GET  /hospitals     → List all hospitals with ward data
GET  /hospitals/{id} → Single hospital details
POST /assign        → AI patient assignment (Gemini)
POST /admit         → Admit patient (reduce bed count)
POST /discharge     → Discharge patient (increase bed count)
```

### Example: Assign Patient

```bash
curl -X POST http://localhost:8000/assign \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "heart attack",
    "severity": "critical",
    "location": "Cheras",
    "age": 55
  }'
```

### Response:
```json
{
  "status": "success",
  "assignment": {
    "hospital_id": "abc123",
    "hospital_name": "Hospital Kuala Lumpur (HKL)",
    "ward_type": "icu",
    "confidence": 0.94,
    "reason": "HKL has cardiac specialty and 3 ICU beds available. Shortest wait time for critical cardiac cases.",
    "urgency_flag": true,
    "estimated_wait": "25 min",
    "alternatives": [...],
    "ai_engine": "gemini-1.5-flash"
  }
}
```

---

## Deploy to Google Cloud Run

```bash
# Build and deploy
gcloud run deploy er-load-balancer \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID

# Get your URL
gcloud run services describe er-load-balancer \
  --region asia-southeast1 \
  --format="value(status.url)"
```

Update the Backend URL in the frontend (`index.html`) with your Cloud Run URL.

---

## Hospital Firestore Schema

```
hospitals/{docId}:
  name: string
  short_name: string
  location: string
  address: string
  wait_time: number (minutes)
  specialties: array<string>
  contact: string
  wards:
    icu:     { available: number, total: number, price_myr: number }
    premium: { available: number, total: number, price_myr: number }
    regular: { available: number, total: number, price_myr: number }
    general: { available: number, total: number, price_myr: number }
```

---

## Firestore Security Rules (paste in Firebase Console)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /hospitals/{hospitalId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

---

## Project Structure

```
er-system/
├── backend/
│   ├── __init__.py
│   ├── main.py        ← FastAPI app, all endpoints
│   ├── database.py    ← Firestore queries
│   └── ai.py         ← Gemini AI assignment logic
├── data/
│   └── seed_hospitals.py  ← Populate Firestore
├── frontend/
│   └── index.html     ← Complete single-file SPA
├── Dockerfile         ← Cloud Run deployment
├── requirements.txt
└── README.md
```