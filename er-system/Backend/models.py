from pydantic import BaseModel

class Patient(BaseModel):
    condition: str
    severity: str
    location: str