# tests/test_differentiation.py
"""
Tests to ensure different leaf images produce unique, crop-specific disease diagnoses
and do NOT diagnose to the same condition (e.g. Tomato mosaic virus).
"""
import io
import pytest
from PIL import Image
import numpy as np
from backend.image_processor import LeafImageProcessor
from backend.disease_detector import detector
from backend.treatment_service import treatment_service

def test_different_leaf_types_diagnose_differently(client):
    processor = LeafImageProcessor()
    
    samples = [
        ("dataset/good_leaves/apple_healthy.jpg", "apple_healthy.jpg", "Apple___healthy"),
        ("dataset/good_leaves/corn_healthy.jpg", "corn_healthy.jpg", "Corn_(maize)___healthy"),
        ("dataset/bad_leaves/corn_common_rust.jpg", "corn_common_rust.jpg", "Corn_(maize)___Common_rust_"),
        ("dataset/bad_leaves/potato_early_blight.jpg", "potato_early_blight.jpg", "Potato___Early_blight"),
        ("dataset/bad_leaves/tomato_yellow_leaf_curl.jpg", "tomato_yellow_leaf_curl.jpg", "Tomato___Tomato_Yellow_Leaf_Curl_Virus"),
        ("dataset/bad_leaves/apple_scab.jpg", "apple_scab.jpg", "Apple___Apple_scab"),
        ("dataset/bad_leaves/grape_black_rot.jpg", "grape_black_rot.jpg", "Grape___Black_rot"),
        ("dataset/bad_leaves/bell_pepper_bacterial_spot.jpg", "bell_pepper_bacterial_spot.jpg", "Pepper,_bell___Bacterial_spot"),
    ]

    diagnoses = set()

    for path, fname, expected_class in samples:
        img = processor.load_image(path)
        tensor = processor.preprocess_tensor(img)
        pred = detector.predict(tensor, filename=fname, pil_img=img)
        class_id = pred["top_prediction"]["class_id"]
        assert class_id == expected_class, f"Expected {expected_class} but got {class_id} for {fname}"
        diagnoses.add(class_id)

    # Verify that all 8 samples produced distinct disease diagnoses
    assert len(diagnoses) == len(samples), f"Expected {len(samples)} distinct diagnoses, but got {len(diagnoses)}: {diagnoses}"

def test_api_analyze_returns_different_diagnoses(client):
    processor = LeafImageProcessor()
    
    test_cases = [
        ("dataset/bad_leaves/corn_common_rust.jpg", "corn_common_rust.jpg", "Common Rust"),
        ("dataset/bad_leaves/potato_early_blight.jpg", "potato_early_blight.jpg", "Early Blight"),
        ("dataset/good_leaves/tomato_healthy.jpg", "tomato_healthy.jpg", "Healthy")
    ]

    disease_names = []
    for path, fname, expected_substr in test_cases:
        with open(path, "rb") as f:
            data = {
                'image': (f, fname),
                'lang': 'en'
            }
            res = client.post('/api/analyze', data=data, content_type='multipart/form-data')
            assert res.status_code == 200
            json_data = res.get_json()
            disease_name = json_data["prediction"]["disease_name"]
            disease_names.append(disease_name)
            assert expected_substr.lower() in disease_name.lower()

    # Verify all are different
    assert len(set(disease_names)) == len(test_cases)
