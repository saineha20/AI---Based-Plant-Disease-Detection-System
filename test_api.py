# tests/test_api.py
"""
Unit and integration tests for Kisan Mitra REST API endpoints.
"""
import pytest
import io
from PIL import Image
import numpy as np

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "languages" in data
    assert "en" in data["languages"]
    assert "hi" in data["languages"]
    assert "te" in data["languages"]
    assert data["model"]["model_loaded"] is True
    assert data["model"]["supported_classes_count"] == 38

def test_model_info_endpoint(client):
    res = client.get('/api/model-info')
    assert res.status_code == 200
    data = res.get_json()
    assert data["classes_count"] == 38
    assert "Tomato___Early_blight" in data["classes"]

def test_diseases_endpoint(client):
    # Test English
    res_en = client.get('/api/diseases?lang=en')
    assert res_en.status_code == 200
    data_en = res_en.get_json()
    assert data_en["total"] == 38

    # Test Telugu
    res_te = client.get('/api/diseases?lang=te')
    assert res_te.status_code == 200
    data_te = res_te.get_json()
    assert data_te["language"] == "te"
    assert len(data_te["diseases"]) == 38

    # Test Hindi
    res_hi = client.get('/api/diseases?lang=hi')
    assert res_hi.status_code == 200
    data_hi = res_hi.get_json()
    assert data_hi["language"] == "hi"

def test_treatment_endpoint(client):
    res = client.get('/api/treatment/Tomato___Early_blight?lang=te')
    assert res.status_code == 200
    data = res.get_json()
    assert data["disease_info"]["id"] == "Tomato___Early_blight"
    assert data["disease_info"]["crop"] == "టమోటా"
    assert len(data["disease_info"]["symptoms"]) > 0
    assert len(data["treatment"]["cultural_controls"]) > 0
    # Crucial agricultural check: fertilizer explanation exists
    assert "fertilizer_guidance" in data["treatment"]
    assert data["treatment"]["fertilizer_guidance"]["is_fertilizer_cure"] is False

def test_translations_endpoint(client):
    res = client.get('/api/translations/te')
    assert res.status_code == 200
    data = res.get_json()
    assert "app_title" in data["translations"]

def test_analyze_missing_file(client):
    res = client.post('/api/analyze')
    assert res.status_code == 400
    data = res.get_json()
    assert data["error_type"] == "missing_file"

def test_analyze_valid_leaf_image(client):
    # Create synthetic leaf image (224x224 RGB, greenish)
    img_arr = np.zeros((224, 224, 3), dtype=np.uint8)
    img_arr[:, :, 1] = 140  # Strong green channel
    img_arr[:, :, 0] = 50   # Red
    img_arr[:, :, 2] = 40   # Blue
    
    img = Image.fromarray(img_arr)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    data = {
        'image': (img_bytes, 'leaf_test.jpg'),
        'lang': 'en'
    }

    res = client.post('/api/analyze', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    result = res.get_json()
    assert result["status"] == "success"
    assert "prediction" in result
    assert "confidence" in result["prediction"]
    assert "disease_info" in result
    assert "treatment" in result

def test_voice_query_endpoint(client):
    # Test Telugu voice query
    payload = {
        "query": "ఈ ఆకుకు ఏ వ్యాధి వచ్చింది?",
        "context": {
            "status": "success",
            "prediction": {
                "crop": "టమోటా",
                "disease_name": "ఎర్లీ బ్లైట్",
                "confidence_percentage": 92.5,
                "is_healthy": False
            }
        },
        "lang": "te"
    }
    res = client.post('/api/voice/query', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "result" in data
    assert "ఎర్లీ బ్లైట్" in data["result"]["response_text"]

