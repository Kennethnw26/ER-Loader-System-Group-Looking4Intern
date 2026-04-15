from google.cloud import firestore

db = firestore.Client(project="er-routing-system")

hospitals = [
    {
        "name": "KL General Hospital",
        "location": "Kuala Lumpur",
        "available_beds": 20,
        "wait_time": 30,
        "specialties": ["cardiac", "trauma", "neurology"]
    },
    {
        "name": "Pantai Hospital KL",
        "location": "Bangsar, Kuala Lumpur",
        "available_beds": 8,
        "wait_time": 15,
        "specialties": ["general", "orthopaedic"]
    },
    {
        "name": "SJMC Subang Jaya",
        "location": "Subang Jaya, Selangor",
        "available_beds": 12,
        "wait_time": 45,
        "specialties": ["cardiac", "oncology", "paediatric"]
    },
    {
        "name": "Hospital Selayang",
        "location": "Selayang, Selangor",
        "available_beds": 35,
        "wait_time": 50,
        "specialties": ["trauma", "hepatology", "general"]
    },
    {
        "name": "Sunway Medical Centre",
        "location": "Petaling Jaya, Selangor",
        "available_beds": 5,
        "wait_time": 20,
        "specialties": ["cardiac", "neurology", "general"]
    }
]

for h in hospitals:
    ref = db.collection("hospitals").add(h)
    print(f"Added: {h['name']}")

print("✅ All hospitals seeded!")