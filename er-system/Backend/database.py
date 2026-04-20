from google.cloud import firestore

db = firestore.Client(database="er-database")

def get_all_hospitals():
    hospitals_ref = db.collection("hospitals")
    docs = hospitals_ref.stream()
    hospitals = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        hospitals.append(data)
    return hospitals

def update_hospital_beds(hospital_id: str, ward_type: str = "general", change: int = -1):
    ref = db.collection("hospitals").document(hospital_id)
    doc = ref.get()
    if doc.exists:
        data = doc.to_dict()
        current = data.get("wards", {}).get(ward_type, {}).get("available", 0)
        new_value = max(0, current + change)
        ref.update({f"wards.{ward_type}.available": new_value})

def log_assignment(patient: dict, result: dict):
    db.collection("assignments").add({
        "patient": patient,
        "result": result,
        "timestamp": firestore.SERVER_TIMESTAMP
    })