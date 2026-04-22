import os
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Lazy import to avoid startup crash if credentials not set
_db = None

def get_db():
    global _db
    if _db is None:
        try:
            from google.cloud import firestore
            # FIX 1: Use actual project ID as fallback instead of placeholder
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "hakcaton-group-looking4intern")
            _db = firestore.Client(project=project_id, database="er-database")
            logger.info(f"Firestore connected to project: {project_id}")
        except Exception as e:
            logger.error(f"Firestore connection failed: {e}")
            raise
    return _db

async def get_hospitals():
    """Fetch all hospitals from Firestore"""
    try:
        db = get_db()
        loop = asyncio.get_running_loop()  # FIX 2: get_event_loop() deprecated in Python 3.10+

        def _fetch():
            hospitals = []
            docs = db.collection("hospitals").stream()
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                hospitals.append(data)
            return hospitals

        hospitals = await loop.run_in_executor(None, _fetch)
        logger.info(f"Fetched {len(hospitals)} hospitals")
        return hospitals
    except Exception as e:
        logger.error(f"get_hospitals error: {e}")
        raise

async def get_hospital_by_id(hospital_id: str):
    """Fetch a single hospital by ID"""
    try:
        db = get_db()
        loop = asyncio.get_running_loop()  # FIX 2

        def _fetch():
            doc = db.collection("hospitals").document(hospital_id).get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            return None

        return await loop.run_in_executor(None, _fetch)
    except Exception as e:
        logger.error(f"get_hospital_by_id error: {e}")
        raise

async def update_hospital_beds(hospital_id: str, ward_type: str, action: str = "admit"):
    """
    Update bed count when patient is admitted or discharged.
    ward_type: icu | premium | regular | general
    action: admit | discharge
    """
    try:
        db = get_db()
        loop = asyncio.get_running_loop()  # FIX 2

        def _update():
            ref = db.collection("hospitals").document(hospital_id)
            doc = ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            wards = data.get("wards", {})
            ward = wards.get(ward_type, {})
            available = ward.get("available", 0)
            total = ward.get("total", 0)
            if action == "admit":
                if available <= 0:
                    return None
                ward["available"] = available - 1
            elif action == "discharge":
                if available < total:
                    ward["available"] = available + 1
            wards[ward_type] = ward
            ref.update({"wards": wards})
            data["wards"] = wards
            data["id"] = hospital_id
            return data

        return await loop.run_in_executor(None, _update)
    except Exception as e:
        logger.error(f"update_hospital_beds error: {e}")
        raise