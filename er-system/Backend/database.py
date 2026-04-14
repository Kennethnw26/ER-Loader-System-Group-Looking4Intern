from google.cloud import firestore

db = firestore.Client()

def get_hospitals():
    hospitals_ref = db.collection("hospitals")
    docs = hospitals_ref.stream()

    hospitals = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        hospitals.append(data)

    return hospitals