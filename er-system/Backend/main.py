from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import PatientInput
from database import get_all_hospitals, update_hospital_beds, log_assignment
from ai import get_routing_decision

app = FastAPI(title="ER Routing System API", version="1.0")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ER Routing System is live ✅"}

@app.get("/hospitals")
def list_hospitals():
    hospitals = get_all_hospitals()
    return {"hospitals": hospitals}

@app.post("/assign")
def assign_patient(patient: PatientInput):
    # 1. Get all hospitals from Firestore
    hospitals = get_all_hospitals()
    
    if not hospitals:
        raise HTTPException(status_code=500, detail="No hospitals in database")
    
    # 2. Ask Gemini to decide
    try:
        decision = get_routing_decision(patient.dict(), hospitals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI routing failed: {str(e)}")
    
    # 3. Update hospital bed count (-1 for new patient)
    try:
        update_hospital_beds(decision["hospital_id"], -1)
    except Exception as e:
        print(f"Warning: Could not update beds: {e}")
    
    # 4. Log the assignment
    log_assignment(patient.dict(), decision)
    
    return {
        "success": True,
        "assignment": decision
    }

@app.get("/assignments")
def get_assignments():
    from database import db
    docs = db.collection("assignments").order_by(
        "timestamp", direction="DESCENDING"
    ).limit(20).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return {"assignments": results}