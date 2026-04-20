import os
import asyncio
import logging
import time
_cache = {"hospitals": None, "timestamp": 0}
CACHE_TTL = 30  # seconds

logger = logging.getLogger(__name__)

_db = None

def get_db():
    global _db
    if _db is None:
        try:
            from google.cloud import firestore
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "hakcaton-group-looking4intern")
            _db = firestore.Client(project=project_id, database="er-database")
            logger.info(f"Firestore connected: project={project_id}, database=er-database")
        except Exception as e:
            logger.error(f"Firestore connection failed: {e}")
            raise
    return _db

async def get_hospitals():
    global _cache
    now = time.time()
    if _cache["hospitals"] and (now - _cache["timestamp"]) < CACHE_TTL:
        logger.info("Returning cached hospitals")
        return _cache["hospitals"]
    try:
        db = get_db()
        loop = asyncio.get_event_loop()

        def _fetch():
            hospitals = []
            docs = db.collection("hospitals").stream()
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                hospitals.append(data)
            return hospitals

        hospitals = await loop.run_in_executor(None, _fetch)
        _cache["hospitals"] = hospitals
        _cache["timestamp"] = now
        logger.info(f"Fetched {len(hospitals)} hospitals from Firestore")
        return hospitals
    except Exception as e:
        logger.error(f"get_hospitals error: {e}")
        raise

async def get_hospital_by_id(hospital_id: str):
    try:
        db = get_db()
        loop = asyncio.get_event_loop()

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
    try:
        db = get_db()
        loop = asyncio.get_event_loop()

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

            # Build return data from what we already have — no second read
            data["wards"] = wards
            data["id"] = hospital_id
            return data

        return await loop.run_in_executor(None, _update)
    except Exception as e:
        logger.error(f"update_hospital_beds error: {e}")
        raise