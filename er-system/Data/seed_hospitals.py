"""
Seed script: populates Firestore with hospital data.
Run: python -m Data.seed_hospitals
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from google.cloud import firestore

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "hakcaton-group-looking4intern")
DATABASE_ID = "er-database"

HOSPITALS = [
    {
        "name": "Hospital Kuala Lumpur (HKL)",
        "short_name": "HKL",
        "location": "Kuala Lumpur",
        "address": "Jalan Pahang, 50586 Kuala Lumpur",
        "wait_time": 25,
        "specialties": ["cardiac", "trauma", "neurology", "oncology", "pediatric"],
        "contact": "+603-2615 5555",
        "image_color": "#0ea5e9",
        "wards": {
            "icu":     {"available": 3,  "total": 8,   "price_myr": 800},
            "premium": {"available": 5,  "total": 20,  "price_myr": 350},
            "regular": {"available": 18, "total": 60,  "price_myr": 150},
            "general": {"available": 40, "total": 120, "price_myr": 50},
        }
    },
    {
        "name": "Pusat Perubatan Universiti Malaya (PPUM)",
        "short_name": "PPUM",
        "location": "Petaling Jaya",
        "address": "Jalan Universiti, 59100 Kuala Lumpur",
        "wait_time": 35,
        "specialties": ["cardiac", "orthopedic", "gastroenterology", "nephrology"],
        "contact": "+603-7949 2333",
        "image_color": "#10b981",
        "wards": {
            "icu":     {"available": 2,  "total": 6,   "price_myr": 750},
            "premium": {"available": 8,  "total": 25,  "price_myr": 320},
            "regular": {"available": 22, "total": 80,  "price_myr": 140},
            "general": {"available": 55, "total": 150, "price_myr": 45},
        }
    },
    {
        "name": "Hospital Ampang",
        "short_name": "HAmpang",
        "location": "Ampang, Selangor",
        "address": "Jalan Mewah Utama, 68000 Ampang, Selangor",
        "wait_time": 20,
        "specialties": ["trauma", "orthopedic", "general surgery", "pediatric"],
        "contact": "+603-4289 3000",
        "image_color": "#f59e0b",
        "wards": {
            "icu":     {"available": 1,  "total": 5,   "price_myr": 700},
            "premium": {"available": 3,  "total": 15,  "price_myr": 300},
            "regular": {"available": 12, "total": 50,  "price_myr": 130},
            "general": {"available": 30, "total": 100, "price_myr": 40},
        }
    },
    {
        "name": "Sunway Medical Centre",
        "short_name": "Sunway",
        "location": "Subang Jaya, Selangor",
        "address": "No 5, Jalan Lagoon Selatan, 47500 Subang Jaya",
        "wait_time": 15,
        "specialties": ["cardiac", "oncology", "neurology", "orthopedic", "IVF"],
        "contact": "+603-7491 9191",
        "image_color": "#8b5cf6",
        "wards": {
            "icu":     {"available": 4,  "total": 10,  "price_myr": 1200},
            "premium": {"available": 10, "total": 40,  "price_myr": 600},
            "regular": {"available": 25, "total": 80,  "price_myr": 280},
            "general": {"available": 15, "total": 60,  "price_myr": 120},
        }
    },
]

def seed():
    print(f"Connecting to project: {PROJECT_ID}, database: {DATABASE_ID}")
    db = firestore.Client(project=PROJECT_ID, database=DATABASE_ID)

    collection = db.collection("hospitals")

    print("Deleting existing documents...")
    for doc in collection.stream():
        doc.reference.delete()
        print(f"  Deleted: {doc.id}")

    print("Adding new hospitals...")
    for hospital in HOSPITALS:
        ref = collection.add(hospital)
        print(f"  Added: {hospital['name']} (ID: {ref[1].id})")

    print(f"\nDone! Seeded {len(HOSPITALS)} hospitals into er-database.")

if __name__ == "__main__":
    seed()