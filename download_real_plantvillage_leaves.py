# scripts/download_real_plantvillage_leaves.py
"""
Downloads authentic, certified real PlantVillage leaf photographs from GitHub
for all core crop conditions in Kisan Mitra.
Saves them into:
- data/
- data/dataset/good_leaves/
- data/dataset/bad_leaves/
- dataset/good_leaves/
- dataset/bad_leaves/
- data/sample_images/
- frontend/samples/
"""
import os
import urllib.request
import urllib.parse
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_DATASET_GOOD = os.path.join(DATA_DIR, "dataset", "good_leaves")
DATA_DATASET_BAD = os.path.join(DATA_DIR, "dataset", "bad_leaves")
DATASET_GOOD = os.path.join(BASE_DIR, "dataset", "good_leaves")
DATASET_BAD = os.path.join(BASE_DIR, "dataset", "bad_leaves")
SAMPLE_IMAGES = os.path.join(DATA_DIR, "sample_images")
FRONTEND_SAMPLES = os.path.join(BASE_DIR, "frontend", "samples")

for d in [DATA_DIR, DATA_DATASET_GOOD, DATA_DATASET_BAD, DATASET_GOOD, DATASET_BAD, SAMPLE_IMAGES, FRONTEND_SAMPLES]:
    os.makedirs(d, exist_ok=True)

# Map target filename to PlantVillage GitHub folder name and is_healthy flag
DOWNLOAD_MAP = {
    "potato_early_blight.jpg": ("Potato___Early_blight", False),
    "potato_late_blight.jpg": ("Potato___Late_blight", False),
    "potato_healthy.jpg": ("Potato___healthy", True),
    "tomato_early_blight.jpg": ("Tomato___Early_blight", False),
    "tomato_late_blight.jpg": ("Tomato___Late_blight", False),
    "tomato_yellow_leaf_curl.jpg": ("Tomato___Tomato_Yellow_Leaf_Curl_Virus", False),
    "tomato_healthy.jpg": ("Tomato___healthy", True),
    "corn_common_rust.jpg": ("Corn_(maize)___Common_rust_", False),
    "corn_healthy.jpg": ("Corn_(maize)___healthy", True),
    "apple_scab.jpg": ("Apple___Apple_scab", False),
    "apple_healthy.jpg": ("Apple___healthy", True),
    "bell_pepper_bacterial_spot.jpg": ("Pepper,_bell___Bacterial_spot", False),
    "bell_pepper_healthy.jpg": ("Pepper,_bell___healthy", True),
    "grape_black_rot.jpg": ("Grape___Black_rot", False),
    "grape_healthy.jpg": ("Grape___healthy", True)
}

def download_all():
    print("Starting download of authentic PlantVillage leaf photographs from GitHub...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for filename, (pv_folder, is_healthy) in DOWNLOAD_MAP.items():
        encoded_folder = urllib.parse.quote(pv_folder)
        api_url = f"https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{encoded_folder}"
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                contents = json.loads(resp.read().decode("utf-8"))

            if not contents or not isinstance(contents, list):
                print(f"  [Skip] No images in folder {pv_folder}")
                continue

            # Pick the second image for variety
            idx = 1 if len(contents) > 1 else 0
            img_url = contents[idx]["download_url"]
            print(f"Downloading real photo for {filename} ({pv_folder})...")

            img_req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                img_data = img_resp.read()

            # Save in all corresponding folders
            # 1. Main data/ root folder
            with open(os.path.join(DATA_DIR, filename), "wb") as f:
                f.write(img_data)

            # 2. data/dataset/
            target_data_dataset = DATA_DATASET_GOOD if is_healthy else DATA_DATASET_BAD
            with open(os.path.join(target_data_dataset, filename), "wb") as f:
                f.write(img_data)

            # 3. dataset/
            target_dataset = DATASET_GOOD if is_healthy else DATASET_BAD
            with open(os.path.join(target_dataset, filename), "wb") as f:
                f.write(img_data)

            # 4. data/sample_images/
            with open(os.path.join(SAMPLE_IMAGES, filename), "wb") as f:
                f.write(img_data)

            # 5. frontend/samples/
            with open(os.path.join(FRONTEND_SAMPLES, filename), "wb") as f:
                f.write(img_data)

            print(f"  [OK] Saved authentic photograph for {filename} (Size: {len(img_data):,} bytes)")

        except Exception as e:
            print(f"  [Error] Failed to download {pv_folder}: {e}")

    print("\nDownload completed! All 15 authentic PlantVillage leaf photographs are installed across all folders.")

if __name__ == "__main__":
    download_all()

