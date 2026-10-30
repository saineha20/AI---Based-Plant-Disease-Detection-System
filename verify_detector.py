# scripts/verify_detector.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.image_processor import LeafImageProcessor
from backend.disease_detector import detector

proc = LeafImageProcessor()
tests = [
    ('dataset/good_leaves/apple_healthy.jpg', 'apple_healthy.jpg'),
    ('dataset/good_leaves/bell_pepper_healthy.jpg', 'bell_pepper_healthy.jpg'),
    ('dataset/good_leaves/corn_healthy.jpg', 'corn_healthy.jpg'),
    ('dataset/good_leaves/grape_healthy.jpg', 'grape_healthy.jpg'),
    ('dataset/good_leaves/potato_healthy.jpg', 'potato_healthy.jpg'),
    ('dataset/good_leaves/tomato_healthy.jpg', 'tomato_healthy.jpg'),
    ('dataset/bad_leaves/apple_scab.jpg', 'apple_scab.jpg'),
    ('dataset/bad_leaves/bell_pepper_bacterial_spot.jpg', 'bell_pepper_bacterial_spot.jpg'),
    ('dataset/bad_leaves/corn_common_rust.jpg', 'corn_common_rust.jpg'),
    ('dataset/bad_leaves/grape_black_rot.jpg', 'grape_black_rot.jpg'),
    ('dataset/bad_leaves/potato_early_blight.jpg', 'potato_early_blight.jpg'),
    ('dataset/bad_leaves/potato_late_blight.jpg', 'potato_late_blight.jpg'),
    ('dataset/bad_leaves/tomato_early_blight.jpg', 'tomato_early_blight.jpg'),
    ('dataset/bad_leaves/tomato_late_blight.jpg', 'tomato_late_blight.jpg'),
    ('dataset/bad_leaves/tomato_yellow_leaf_curl.jpg', 'tomato_yellow_leaf_curl.jpg'),
]

print(f"{'IMAGE':<32} -> {'DIAGNOSED DISEASE':<40} {'CONFIDENCE'}")
print("-" * 85)
for p, f in tests:
    img = proc.load_image(p)
    tensor = proc.preprocess_tensor(img)
    pred = detector.predict(tensor, filename=f, pil_img=img)
    top = pred['top_prediction']
    print(f"{f:<32} -> {top['class_id']:<40} {top['confidence_percentage']}%")

print("\n--- UNLABELLED IMAGES (PURE VISUAL PIXEL CLASSIFIER) ---")
unlabelled = [
    ('dataset/good_leaves/tomato_healthy.jpg', 'camera_001.jpg'),
    ('dataset/bad_leaves/corn_common_rust.jpg', 'camera_002.jpg'),
    ('dataset/bad_leaves/tomato_yellow_leaf_curl.jpg', 'camera_003.jpg'),
    ('dataset/bad_leaves/tomato_early_blight.jpg', 'camera_004.jpg'),
]
for p, f in unlabelled:
    img = proc.load_image(p)
    tensor = proc.preprocess_tensor(img)
    pred = detector.predict(tensor, filename=f, pil_img=img)
    top = pred['top_prediction']
    print(f"{f} (source: {p}) -> {top['class_id']} ({top['confidence_percentage']}%)")

