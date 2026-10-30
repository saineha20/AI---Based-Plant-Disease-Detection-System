# tests/test_image_validation.py
"""
Unit tests for image file validation, corrupted file rejection, and quality checking.
"""
import io
import pytest
from PIL import Image
import numpy as np

from backend.validators import validate_image_file, ValidationError, sanitize_filename
from backend.image_processor import LeafImageProcessor, ImageProcessingError

class DummyFileStorage:
    def __init__(self, filename, stream):
        self.filename = filename
        self.stream = stream

def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd.jpg") == "passwd.jpg"
    assert sanitize_filename("my leaf photo!.png") == "my_leaf_photo_.png"
    assert sanitize_filename("") == "leaf_upload.jpg"

def test_valid_jpeg_header():
    # Valid JPEG header
    img = Image.new("RGB", (150, 150), color=(50, 160, 50))
    stream = io.BytesIO()
    img.save(stream, format="JPEG")
    stream.seek(0)

    f = DummyFileStorage("test_leaf.jpg", stream)
    res = validate_image_file(f)
    assert res["valid"] is True
    assert res["extension"] == "jpg"

def test_invalid_extension():
    stream = io.BytesIO(b"fake data" * 200)
    f = DummyFileStorage("script.exe", stream)
    with pytest.raises(ValidationError) as exc:
        validate_image_file(f)
    assert "Unsupported file extension" in str(exc.value)

def test_file_too_small():
    stream = io.BytesIO(b"tiny")
    f = DummyFileStorage("leaf.jpg", stream)
    with pytest.raises(ValidationError) as exc:
        validate_image_file(f)
    assert "too small" in str(exc.value)

def test_corrupted_header():
    # File named .jpg with > 1KB size but invalid binary header
    stream = io.BytesIO(b"NOT_A_JPEG_HEADER_" + (b"A" * 2048))
    f = DummyFileStorage("fake.jpg", stream)
    with pytest.raises(ValidationError) as exc:
        validate_image_file(f)
    assert "does not match a valid" in str(exc.value)

def test_quality_checks_blurriness():
    processor = LeafImageProcessor()
    # A completely flat, uniform color image has zero Laplacian variance (blurry)
    flat_img = Image.new("RGB", (200, 200), color=(80, 80, 80))
    q = processor.assess_quality(flat_img)
    assert q["acceptable"] is False
    assert any("blurry" in w.lower() for w in q["warnings"])

def test_quality_checks_darkness():
    processor = LeafImageProcessor()
    # Very dark image (mean brightness < 20)
    dark_img = Image.new("RGB", (200, 200), color=(5, 5, 5))
    q = processor.assess_quality(dark_img)
    assert q["acceptable"] is False
    assert any("dark" in w.lower() for w in q["warnings"])

def test_tensor_preprocessing_shape():
    processor = LeafImageProcessor(target_size=(224, 224))
    img = Image.new("RGB", (300, 400), color=(40, 150, 40))
    tensor_nchw = processor.preprocess_tensor(img, layout="NCHW")
    assert tensor_nchw.shape == (1, 3, 224, 224)
    assert tensor_nchw.dtype == np.float32

    tensor_nhwc = processor.preprocess_tensor(img, layout="NHWC")
    assert tensor_nhwc.shape == (1, 224, 224, 3)
