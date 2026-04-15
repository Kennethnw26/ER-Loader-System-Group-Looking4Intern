from pydantic import BaseModel
from typing import Optional

class PatientInput(BaseModel):
    condition: str
    severity: str          # low / medium / high / critical
    location: str
    age: Optional[int] = None
    notes: Optional[str] = None

class HospitalAssignment(BaseModel):
    assigned_hospital: str
    hospital_id: str
    reason: str
    estimated_wait: str
    severity_flag: str