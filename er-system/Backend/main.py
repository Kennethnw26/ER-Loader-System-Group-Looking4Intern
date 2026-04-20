from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import logging

from .database import get_hospitals, get_hospital_by_id, update_hospital_beds
from .ai import assign_patient_to_hospital

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ER Load Balancer API",
    description="AI-powered emergency room patient distribution system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatientRequest(BaseModel):
    condition: str
    severity: str
    location: Optional[str] = None
    age: Optional[int] = None
    notes: Optional[str] = None

class AdmitPatientRequest(BaseModel):
    hospital_id: str
    ward_type: str
    patient_name: Optional[str] = None
    condition: str
    severity: str

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "ER Load Balancer",
        "version": "1.0.0",
        "endpoints": ["/hospitals", "/assign", "/hospitals/{id}", "/admit"]
    }

@app.get("/hospitals")
async def list_hospitals():
    try:
        hospitals = await get_hospitals()
        return {"status": "success", "count": len(hospitals), "hospitals": hospitals}
    except Exception as e:
        logger.error(f"Error fetching hospitals: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/hospitals/{hospital_id}")
async def get_hospital(hospital_id: str):
    try:
        hospital = await get_hospital_by_id(hospital_id)
        if not hospital:
            raise HTTPException(status_code=404, detail="Hospital not found")
        return {"status": "success", "hospital": hospital}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching hospital {hospital_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/assign")
async def assign_patient(patient: PatientRequest):
    try:
        hospitals = await get_hospitals()
        if not hospitals:
            raise HTTPException(status_code=503, detail="No hospitals available")
        result = await assign_patient_to_hospital(patient.dict(), hospitals)
        return {"status": "success", "assignment": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning patient: {e}")
        raise HTTPException(status_code=500, detail=f"Assignment error: {str(e)}")

@app.post("/admit")
async def admit_patient(req: AdmitPatientRequest):
    try:
        result = await update_hospital_beds(req.hospital_id, req.ward_type, action="admit")
        if not result:
            raise HTTPException(status_code=400, detail="No beds available in that ward")
        return {"status": "success", "message": "Patient admitted", "updated": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error admitting patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/discharge")
async def discharge_patient(hospital_id: str, ward_type: str):
    try:
        result = await update_hospital_beds(hospital_id, ward_type, action="discharge")
        return {"status": "success", "message": "Patient discharged", "updated": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/app")
async def serve_frontend():
    return FileResponse("Frontend/index.html")