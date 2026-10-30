# backend/treatment_service.py
"""
Agricultural Advisory & Treatment Service
Provides verified crop disease info, cultural controls, biological inputs,
chemical guidance, fertilizer reality checks, and safety precautions.
Uses SQLite database (data/kisan_mitra.db) with fallback to JSON files.
"""
import os
import json
import logging
from backend.database import (
    init_database,
    query_disease_by_id,
    query_treatment_by_id,
    query_all_diseases
)

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DISEASES_PATH = os.path.join(DATA_DIR, "diseases.json")
TREATMENTS_PATH = os.path.join(DATA_DIR, "treatments.json")

class TreatmentService:
    def __init__(self):
        try:
            init_database()
            self.use_db = True
        except Exception as e:
            logger.warning(f"Could not initialize SQLite database, using JSON fallback: {e}")
            self.use_db = False

        self.diseases = self._load_json(DISEASES_PATH)
        self.treatments = self._load_json(TREATMENTS_PATH)

    def _load_json(self, path) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {path}: {e}")
        return {}

    def get_supported_diseases_list(self, lang="en") -> list:
        """Returns catalog of all supported crops and diseases."""
        lang = lang if lang in ["en", "hi", "te"] else "en"
        if self.use_db:
            try:
                return query_all_diseases(lang=lang)
            except Exception as e:
                logger.warning(f"Database query error, falling back to JSON: {e}")

        # JSON Fallback
        catalog = []
        for d_id, d in self.diseases.items():
            crop_name = d.get("crop", {}).get(lang) or d.get("crop", {}).get("en")
            disease_name = d.get("disease_name", {}).get(lang) or d.get("disease_name", {}).get("en")
            catalog.append({
                "id": d_id,
                "crop": crop_name,
                "disease_name": disease_name,
                "is_healthy": d.get("is_healthy", False),
                "pathogen_type": d.get("pathogen_type", "unknown")
            })
        return sorted(catalog, key=lambda x: (x["crop"], x["disease_name"]))

    def get_disease_info(self, disease_id: str, lang="en") -> dict:
        """Returns crop and disease details localized to the requested language."""
        lang = lang if lang in ["en", "hi", "te"] else "en"
        if self.use_db:
            try:
                res = query_disease_by_id(disease_id, lang=lang)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Database query error for {disease_id}: {e}")

        # JSON Fallback
        d = self.diseases.get(disease_id)
        if not d:
            return None

        return {
            "id": disease_id,
            "crop": d.get("crop", {}).get(lang) or d.get("crop", {}).get("en"),
            "disease_name": d.get("disease_name", {}).get(lang) or d.get("disease_name", {}).get("en"),
            "pathogen_type": d.get("pathogen_type", "unknown"),
            "scientific_name": d.get("scientific_name", "N/A"),
            "is_healthy": d.get("is_healthy", False),
            "summary": d.get("summary", {}).get(lang) or d.get("summary", {}).get("en"),
            "symptoms": d.get("symptoms", {}).get(lang) or d.get("symptoms", {}).get("en", []),
            "favorable_conditions": d.get("favorable_conditions", {}).get(lang) or d.get("favorable_conditions", {}).get("en", []),
            "immediate_actions": d.get("immediate_actions", {}).get(lang) or d.get("immediate_actions", {}).get("en", [])
        }

    def get_treatment_info(self, disease_id: str, lang="en") -> dict:
        """Returns treatment protocol localized to the requested language."""
        lang = lang if lang in ["en", "hi", "te"] else "en"
        if self.use_db:
            try:
                res = query_treatment_by_id(disease_id, lang=lang)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Database query error for treatment {disease_id}: {e}")

        # JSON Fallback
        t = self.treatments.get(disease_id)
        if not t:
            return None

        fert = t.get("fertilizer_guidance", {})
        fert_explanation = fert.get("explanation", {}).get(lang) or fert.get("explanation", {}).get("en", "")

        return {
            "disease_id": disease_id,
            "cultural_controls": t.get("cultural_controls", {}).get(lang) or t.get("cultural_controls", {}).get("en", []),
            "organic_controls": t.get("organic_controls", {}).get(lang) or t.get("organic_controls", {}).get("en", []),
            "chemical_controls": t.get("chemical_controls", {}).get(lang) or t.get("chemical_controls", {}).get("en", []),
            "fertilizer_guidance": {
                "is_fertilizer_cure": fert.get("is_fertilizer_cure", False),
                "explanation": fert_explanation
            },
            "safety_precautions": t.get("safety_precautions", {}).get(lang) or t.get("safety_precautions", {}).get("en", []),
            "expert_consultation": t.get("expert_consultation", {}).get(lang) or t.get("expert_consultation", {}).get("en", "")
        }

    def build_analysis_report(self, prediction: dict, quality: dict, lang="en") -> dict:
        """Combines ML prediction, quality check, disease metadata, and treatments into a unified report."""
        lang = lang if lang in ["en", "hi", "te"] else "en"
        top = prediction["top_prediction"]
        class_id = top["class_id"]

        disease_info = self.get_disease_info(class_id, lang=lang)
        treatment_info = self.get_treatment_info(class_id, lang=lang)

        # Localize alternatives
        localized_alternatives = []
        for alt in prediction.get("alternatives", []):
            alt_info = self.get_disease_info(alt["class_id"], lang=lang)
            if alt_info:
                localized_alternatives.append({
                    "class_id": alt["class_id"],
                    "crop": alt_info["crop"],
                    "disease_name": alt_info["disease_name"],
                    "confidence": alt["confidence"],
                    "confidence_percentage": alt["confidence_percentage"]
                })

        # Fallback if class_id is unrecognized
        if not disease_info:
            disease_info = {
                "id": class_id,
                "crop": "Unrecognized Crop",
                "disease_name": class_id.replace("___", " ").replace("_", " "),
                "pathogen_type": "unknown",
                "scientific_name": "N/A",
                "is_healthy": False,
                "summary": "The leaf condition is outside the standard certified categories.",
                "symptoms": ["Atypical leaf pattern detected."],
                "favorable_conditions": [],
                "immediate_actions": ["Consult local agricultural officer for manual leaf diagnosis."]
            }

        return {
            "status": "success",
            "language": lang,
            "prediction": {
                "class_id": class_id,
                "crop": disease_info["crop"],
                "disease_name": disease_info["disease_name"],
                "confidence": top["confidence"],
                "confidence_percentage": top["confidence_percentage"],
                "is_healthy": disease_info["is_healthy"],
                "confidence_rating": prediction["confidence_rating"],
                "diagnosis_status": prediction["diagnosis_status"],
                "is_fine_tuned": prediction.get("is_fine_tuned", False)
            },
            "alternatives": localized_alternatives,
            "quality": quality,
            "disease_info": disease_info,
            "treatment": treatment_info
        }

# Global instance
treatment_service = TreatmentService()
