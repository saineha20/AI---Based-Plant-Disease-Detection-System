# tests/test_database.py
"""
Unit tests for SQLite database operations in backend/database.py.
"""
import pytest
from backend.database import (
    init_database,
    query_disease_by_id,
    query_treatment_by_id,
    query_all_diseases,
    save_diagnosis_to_db,
    get_diagnosis_history_from_db,
    clear_diagnosis_history_db,
    save_farmer_feedback_db
)

@pytest.fixture(autouse=True)
def setup_db():
    init_database()

def test_database_initialization():
    diseases = query_all_diseases(lang="en")
    assert len(diseases) == 38
    assert any(d["id"] == "Tomato___Early_blight" for d in diseases)

def test_query_disease_multilingual():
    # English
    d_en = query_disease_by_id("Tomato___Early_blight", lang="en")
    assert d_en["crop"] == "Tomato"
    assert d_en["disease_name"] == "Early Blight"
    assert d_en["pathogen_type"] == "fungal"
    assert len(d_en["symptoms"]) > 0

    # Telugu
    d_te = query_disease_by_id("Tomato___Early_blight", lang="te")
    assert d_te["crop"] == "టమోటా"
    assert "ముందస్తు ముడత" in d_te["disease_name"]

    # Hindi
    d_hi = query_disease_by_id("Tomato___Early_blight", lang="hi")
    assert d_hi["crop"] == "टमाटर"
    assert "अगेती झुलसा" in d_hi["disease_name"]

def test_query_treatment():
    t_en = query_treatment_by_id("Tomato___Early_blight", lang="en")
    assert t_en is not None
    assert len(t_en["cultural_controls"]) > 0
    assert len(t_en["chemical_controls"]) > 0
    assert t_en["fertilizer_guidance"]["is_fertilizer_cure"] is False
    assert "fertilizers do not cure" in t_en["fertilizer_guidance"]["explanation"].lower()

def test_diagnosis_history_flow():
    clear_diagnosis_history_db()

    rec_id = save_diagnosis_to_db({
        "disease_id": "Tomato___Early_blight",
        "crop": "Tomato",
        "disease_name": "Early Blight",
        "confidence": 94.5,
        "confidence_rating": "high",
        "diagnosis_status": "disease_detected",
        "language": "en",
        "thumbnail": "sample_thumbnail",
        "quality_metrics": {"brightness": 120, "sharpness": 85}
    })
    assert rec_id > 0

    history = get_diagnosis_history_from_db(limit=10)
    assert len(history) == 1
    assert history[0]["crop"] == "Tomato"
    assert history[0]["confidence"] == 94.5

    # Test feedback
    f_id = save_farmer_feedback_db(
        diagnosis_id=rec_id,
        is_accurate=True,
        comments="Very accurate diagnosis, sprayed Mancozeb as advised."
    )
    assert f_id > 0

    # Test clear
    clear_diagnosis_history_db()
    assert len(get_diagnosis_history_from_db()) == 0

