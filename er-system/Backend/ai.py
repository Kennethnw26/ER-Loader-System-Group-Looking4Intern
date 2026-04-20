import vertexai
from vertexai.generative_models import GenerativeModel
import json
import os
from dotenv import load_dotenv

load_dotenv()

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_REGION")
)

model = GenerativeModel("gemini-1.5-flash")

def build_prompt(patient: dict, hospitals: list) -> str:
    hospital_list = ""
    for i, h in enumerate(hospitals, 1):
        wards = h.get('wards', {})
        general_beds = wards.get('general', {}).get('available', 0)
        icu_beds = wards.get('icu', {}).get('available', 0)
        total_available = general_beds + icu_beds

        hospital_list += f"""
{i}. {h['name']} ({h.get('short_name', '')})
   - General beds available: {general_beds}
   - ICU beds available: {icu_beds}
   - Total available: {total_available}
   - Wait time: {h['wait_time']} mins
   - Specialties: {', '.join(h.get('specialties', []))}
   - Location: {h['location']}
   - Address: {h.get('address', 'N/A')}
   - Hospital ID: {h['id']}
"""

    prompt = f"""
You are an emergency hospital routing AI for Malaysia.

Your job is to assign the patient to the BEST hospital based on:
1. Medical urgency and specialty match
2. Available beds (NEVER assign to a hospital with 0 beds)
3. Wait time (lower is better for critical cases)
4. Distance relevance to patient location

Patient Details:
- Condition: {patient['condition']}
- Severity: {patient['severity']}
- Location: {patient['location']}
- Age: {patient.get('age', 'Unknown')}
- Notes: {patient.get('notes', 'None')}

Available Hospitals:
{hospital_list}

RULES:
- If severity is "critical", prioritize specialty match over distance
- If a hospital has 0 available beds, do NOT assign to it
- If all hospitals are full, assign to the least busy one and flag it

Return ONLY valid JSON (no extra text):
{{
  "assigned_hospital": "hospital name",
  "hospital_id": "exact hospital id from the list",
  "reason": "clear explanation for the assignment",
  "estimated_wait": "X mins",
  "severity_flag": "normal / urgent / critical-override"
}}
"""
    return prompt

def get_routing_decision(patient: dict, hospitals: list) -> dict:
    prompt = build_prompt(patient, hospitals)
    response = model.generate_content(prompt)
    
    # Clean response and parse JSON
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    
    return json.loads(text.strip())