import os
import json
import logging

logger = logging.getLogger(__name__)


async def assign_patient_to_hospital(patient: dict, hospitals: list) -> dict:
    try:
        return await _gemini_assign(patient, hospitals)
    except Exception as e:
        logger.warning(f"Gemini unavailable, using fallback: {e}")
        return _rule_based_assign(patient, hospitals)


async def _gemini_assign(patient: dict, hospitals: list) -> dict:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    import asyncio

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "hakcaton-group-looking4intern")
    location = os.environ.get("VERTEX_AI_LOCATION", "us-central1")

    hospital_summary = []
    for h in hospitals:
        wards = h.get("wards", {})
        total_available = sum(w.get("available", 0) for w in wards.values())
        hospital_summary.append({
            "id": h.get("id"),
            "name": h.get("name"),
            "location": h.get("location"),
            "wait_time_minutes": h.get("wait_time", 30),
            "specialties": h.get("specialties", []),
            "total_available_beds": total_available,
            "wards": {k: {"available": v.get("available", 0), "total": v.get("total", 0)} for k, v in wards.items()}
        })

    prompt = f"""You are an emergency room triage AI assistant for Malaysian hospitals.

PATIENT INFORMATION:
- Condition: {patient.get('condition', 'unknown')}
- Severity: {patient.get('severity', 'medium')} (scale: low < medium < high < critical)
- Location: {patient.get('location', 'unspecified')}
- Age: {patient.get('age', 'unknown')}
- Additional notes: {patient.get('notes', 'none')}

AVAILABLE HOSPITALS:
{json.dumps(hospital_summary, indent=2)}

TASK: Assign the patient to the BEST hospital. Consider severity, specialties, bed availability, and wait time.

Respond ONLY with valid JSON in this exact format:
{{
  "hospital_id": "<firestore document id>",
  "hospital_name": "<name>",
  "ward_type": "<icu|premium|regular|general>",
  "confidence": <0.0-1.0>,
  "reason": "<clear 1-2 sentence explanation>",
  "urgency_flag": <true|false>,
  "estimated_wait": "<wait time>",
  "alternatives": [
    {{"hospital_name": "<alt1>", "reason": "<brief reason>"}}
  ]
}}"""

    def _call_gemini():
        vertexai.init(project=project_id, location=location)
        model = GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 1024}
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _call_gemini)
    result["ai_engine"] = "gemini-1.5-flash"
    return result


def _rule_based_assign(patient: dict, hospitals: list) -> dict:
    severity = patient.get("severity", "medium").lower()
    condition = patient.get("condition", "").lower()

    if severity == "critical":
        preferred_ward = "icu"
    elif severity == "high":
        preferred_ward = "premium"
    elif severity == "medium":
        preferred_ward = "regular"
    else:
        preferred_ward = "general"

    scored = []
    for h in hospitals:
        score = 0
        wards = h.get("wards", {})
        ward = wards.get(preferred_ward, {})
        available = ward.get("available", 0)

        if available <= 0:
            continue

        specialties = [s.lower() for s in h.get("specialties", [])]
        if any(kw in condition for kw in ["heart", "cardiac", "chest"]) and "cardiac" in specialties:
            score += 30
        if any(kw in condition for kw in ["trauma", "accident", "injury"]) and "trauma" in specialties:
            score += 30
        if any(kw in condition for kw in ["child", "pediatric", "baby"]) and "pediatric" in specialties:
            score += 30

        score += min(available * 5, 30)
        wait = h.get("wait_time", 60)
        score += max(0, 30 - wait // 2)
        scored.append((score, h))

    if not scored:
        scored = [(0, h) for h in hospitals]

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]

    return {
        "hospital_id": best.get("id"),
        "hospital_name": best.get("name"),
        "ward_type": preferred_ward,
        "confidence": 0.75,
        "reason": f"Selected based on {preferred_ward.upper()} ward availability and specialty match for '{patient.get('condition')}'.",
        "urgency_flag": severity in ("critical", "high"),
        "estimated_wait": f"{best.get('wait_time', 30)} min",
        "alternatives": [{"hospital_name": h.get("name"), "reason": "Alternative option"} for _, h in scored[1:3]],
        "ai_engine": "rule-based-fallback"
    }