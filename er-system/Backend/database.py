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

def update_hospital_beds(hospital_id: str, change: int):
    ref = db.collection("hospitals").document(hospital_id)
    doc = ref.get()
    if doc.exists:
        current = doc.to_dict().get("available_beds", 0)
        ref.update({"available_beds": current + change})

def log_assignment(patient: dict, result: dict):
    db.collection("assignments").add({
        "patient": patient,
        "result": result,
        "timestamp": firestore.SERVER_TIMESTAMP
    })