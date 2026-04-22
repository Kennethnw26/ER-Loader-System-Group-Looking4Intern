# 🏥 ER Load Balancer System
**Track 3: Vital Signs (Healthcare & Wellbeing)**
MyAI Future Hackathon Team Looking4Intern

Contributors: Edbert Felo Tjuganda, Richmond Deanlim, Willy Candra, Kenneth Nathaniel Wong

---

## 🌐 Live Application
**Public URL:** https://er-load-balancer-175772493560.asia-southeast1.run.app/app

> Fully accessible without login. No credentials required.

**API Base:** https://er-load-balancer-175772493560.asia-southeast1.run.app

---

## 📋 Problem Statement

As Malaysia transitions toward **"Aged Society"** status, the public healthcare system faces unprecedented strain. Emergency Departments are critically overcrowded while nearby hospitals have underutilised capacity. There is no intelligent system to distribute incoming patients based on real-time bed availability, medical specialties, and wait times — leading to preventable delays and deteriorating patient outcomes.

---

## 💡 Our Solution

The **ER Load Balancer** is an AI-powered patient routing system that moves beyond simple chat to **autonomous action**. Given a patient's condition, severity, and location, the system:

1. Fetches real-time hospital data from Firestore
2. Sends patient + hospital data to **Gemini 1.5 Flash** via Vertex AI
3. Receives an AI-reasoned decision on the optimal hospital and ward
4. Returns a structured assignment with confidence score, full reasoning, and alternatives

This demonstrates the complete **Chat → Action** pipeline required by the hackathon.

---

## 🧰 Google AI Ecosystem Stack

| Component | Technology | Role |
|-----------|-----------|------|
| 🧠 Intelligence | Gemini 1.5 Flash (Vertex AI) | Core AI decision engine |
| 🎯 Orchestrator | Vertex AI Agent Builder | Agentic workflow orchestration |
| 🗄️ Database | Google Cloud Firestore | Real-time hospital and bed data |
| 🚀 Deployment | Google Cloud Run | Serverless backend hosting |
| 🔍 Context | Vertex AI Search (RAG) | Grounded medical data retrieval |
| 🛠️ Dev Tools | Google AI Studio + Antigravity | Prompt testing and deployment |

---

## ✨ Key Features

- **Real-time Hospital Dashboard** — Live bed counts across ICU, Premium, Regular, and General wards for 4 Malaysian hospitals
- **AI Patient Assignment** — Gemini AI recommends the optimal hospital with full reasoning, confidence score, and alternatives
- **Autonomous Decision Making** — Moves beyond chat to take action: receives input → queries database → calls Gemini → returns decision
- **Automatic Fallback** — Rule-based logic activates if Gemini is unavailable, ensuring 100% uptime
- **Edge Case Handling** — Full ward detection, emergency override for critical cases, medical specialty matching
- **Live Network Stats** — Total available beds, ICU free count, average wait time across the network

---

## 🏗️ System Architecture

```
Browser (Frontend — index.html)
            ↓
FastAPI Backend (Google Cloud Run)
        ↓               ↓
Firestore           Gemini 1.5 Flash
(er-database)       (Vertex AI)
        ↓               ↓
  Real-time        AI Reasoning
  Bed Counts       + Decision
```

---

## 📁 Project Structure

```
er-system/
├── Backend/
│   ├── __init__.py      ← Package marker
│   ├── main.py          ← FastAPI app, all API endpoints
│   ├── database.py      ← Firestore queries (er-database)
│   ├── ai.py            ← Gemini AI assignment logic + fallback
│   └── models.py        ← Pydantic data models
├── Data/
│   └── seed_hospitals.py  ← One-time Firestore seeding script
├── Frontend/
│   └── index.html         ← Complete single-file SPA (HTML + CSS + JS)
├── Dockerfile             ← Cloud Run container configuration
├── requirements.txt       ← Python dependencies
└── README.md
```

---

## 🚀 Local Setup Instructions

### Prerequisites
- Python 3.11+
- Google Cloud account with billing enabled
- gcloud CLI installed

### 1. Clone the repository
```bash
git clone https://github.com/Kennethnw26/ER-Loader-System-Group-Looking4Intern.git
cd ER-Loader-System-Group-Looking4Intern/er-system
```

### 2. Create virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. Authenticate with Google Cloud
```bash
gcloud auth login
gcloud config set project hakcaton-group-looking4intern
gcloud auth application-default login
gcloud auth application-default set-quota-project hakcaton-group-looking4intern
```

### 4. Enable required APIs
```bash
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 5. Seed Firestore database
```powershell
$env:GOOGLE_CLOUD_PROJECT = "hakcaton-group-looking4intern"
python -m Data.seed_hospitals
```

### 6. Run locally
```bash
uvicorn Backend.main:app --reload --port 8000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| GET | /hospitals | All hospitals with real-time ward data |
| GET | /hospitals/{id} | Single hospital details |
| POST | /assign | AI patient assignment via Gemini |
| POST | /admit | Admit patient — reduces bed count |
| POST | /discharge | Discharge patient — increases bed count |
| GET | /app | Serves the frontend UI |
| GET | /docs | Interactive API documentation |

### Example: AI Patient Assignment

Request:
```json
POST /assign
{
  "condition": "heart attack",
  "severity": "critical",
  "location": "Cheras",
  "age": 55
}
```

Response:
```json
{
  "status": "success",
  "assignment": {
    "hospital_name": "Hospital Kuala Lumpur (HKL)",
    "ward_type": "icu",
    "confidence": 0.94,
    "reason": "HKL has cardiac specialty and 3 ICU beds available. Shortest wait time for critical cardiac cases.",
    "urgency_flag": true,
    "estimated_wait": "25 min",
    "ai_engine": "gemini-1.5-flash"
  }
}
```

---

## 🏥 Hospital Network

| Hospital | Location | Key Specialties |
|----------|----------|----------------|
| Hospital Kuala Lumpur (HKL) | Kuala Lumpur | Cardiac, Trauma, Neurology, Oncology, Pediatric |
| Pusat Perubatan Universiti Malaya (PPUM) | Petaling Jaya | Cardiac, Orthopedic, Gastroenterology, Nephrology |
| Hospital Ampang | Ampang, Selangor | Trauma, Orthopedic, General Surgery, Pediatric |
| Sunway Medical Centre | Subang Jaya, Selangor | Cardiac, Oncology, Neurology, Orthopedic |

---

## 👥 Team
**Name:** Looking4Intern
**Track:** Track 3 — Vital Signs (Healthcare & Wellbeing)
**Event:** MyAI Future Hackathon, Malaysia
