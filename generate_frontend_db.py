# scripts/generate_frontend_db.py
"""
Generates frontend/disease_database.js containing all 38 PlantVillage crop conditions
with full multilingual translations (English, Hindi, Telugu), clinical summaries,
symptoms, and certified treatment regimens.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISEASES_PATH = os.path.join(BASE_DIR, "data", "diseases.json")
TREATMENTS_PATH = os.path.join(BASE_DIR, "data", "treatments.json")
OUTPUT_JS_PATH = os.path.join(BASE_DIR, "frontend", "disease_database.js")

def generate():
    with open(DISEASES_PATH, "r", encoding="utf-8") as f:
        diseases = json.load(f)
    with open(TREATMENTS_PATH, "r", encoding="utf-8") as f:
        treatments = json.load(f)

    full_kb = {}
    for d_id, d in diseases.items():
        t = treatments.get(d_id, {})
        full_kb[d_id] = {
            "id": d_id,
            "crop": d.get("crop", {}),
            "disease_name": d.get("disease_name", {}),
            "pathogen_type": d.get("pathogen_type", "fungal"),
            "scientific_name": d.get("scientific_name", "N/A"),
            "is_healthy": d.get("is_healthy", False),
            "summary": d.get("summary", {}),
            "symptoms": d.get("symptoms", {}),
            "favorable_conditions": d.get("favorable_conditions", {}),
            "immediate_actions": d.get("immediate_actions", {}),
            "cultural_controls": t.get("cultural_controls", {}),
            "organic_controls": t.get("organic_controls", {}),
            "chemical_controls": t.get("chemical_controls", {}),
            "fertilizer_guidance": t.get("fertilizer_guidance", {
                "is_fertilizer_cure": False,
                "explanation": {
                    "en": "Fertilizers do not cure diseases.",
                    "hi": "उर्वरक बीमारी का इलाज नहीं कर सकते।",
                    "te": "ఎరువులు వ్యాధిని నయం చేయలేవు."
                }
            }),
            "safety_precautions": t.get("safety_precautions", {}),
            "expert_consultation": t.get("expert_consultation", {})
        }

    js_content = "/**\n * Kisan Mitra - Complete 38-Class Multilingual Agricultural Database\n"
    js_content += " * Automatically generated for offline & direct-browser execution\n */\n"
    js_content += "window.KISAN_DISEASE_DB = " + json.dumps(full_kb, ensure_ascii=False, indent=2) + ";\n"

    with open(OUTPUT_JS_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"Generated {OUTPUT_JS_PATH} with {len(full_kb)} diseases.")

if __name__ == "__main__":
    generate()

