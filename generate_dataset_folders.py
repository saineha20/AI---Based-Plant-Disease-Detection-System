# scripts/generate_dataset_folders.py
"""
Generates organized Good Leaves and Bad Leaves datasets.
Creates:
  dataset/good_leaves/
  dataset/bad_leaves/
  data/dataset/good_leaves/
  data/dataset/bad_leaves/
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_ROOTS = [
    os.path.join(BASE_DIR, "dataset"),
    os.path.join(BASE_DIR, "data", "dataset")
]

def make_dirs():
    for root in DATASET_ROOTS:
        os.makedirs(os.path.join(root, "good_leaves"), exist_ok=True)
        os.makedirs(os.path.join(root, "bad_leaves"), exist_ok=True)

def save_to_both(img, category, filename):
    for root in DATASET_ROOTS:
        dest = os.path.join(root, category, filename)
        img.save(dest, "JPEG", quality=92)
    print(f"Saved: {category}/{filename}")

def draw_leaf_base(width=600, height=600, leaf_color=(46, 125, 50), shape_type="oval"):
    img = Image.new("RGB", (width, height), (240, 242, 240))
    draw = ImageDraw.Draw(img)
    cx, cy = width // 2, height // 2

    points = []
    num_pts = 60
    if shape_type == "oval":
        for i in range(num_pts):
            angle = (2 * math.pi * i) / num_pts
            r = 210 * (1.0 - 0.45 * math.cos(angle)) * math.sin(angle / 2.0)
            x = cx + r * math.sin(angle)
            y = cy + r * math.cos(angle) * 1.3 - 20
            points.append((x, y))
        draw.polygon(points, fill=leaf_color, outline=(25, 80, 30))
        # Main vein
        draw.line([(cx, cy - 200), (cx, cy + 190)], fill=(76, 175, 80), width=4)
        for vy in range(cy - 140, cy + 140, 35):
            draw.line([(cx, vy), (cx - 70, vy - 25)], fill=(65, 155, 70), width=2)
            draw.line([(cx, vy), (cx + 70, vy - 25)], fill=(65, 155, 70), width=2)

    elif shape_type == "long": # Corn
        draw.polygon([(180, 50), (420, 50), (370, 550), (230, 550)], fill=leaf_color, outline=(25, 80, 30))
        draw.line([(300, 50), (300, 550)], fill=(120, 185, 100), width=6)
        for vy in range(90, 500, 30):
            draw.line([(300, vy), (200, vy + 40)], fill=(90, 160, 75), width=2)
            draw.line([(300, vy), (400, vy + 40)], fill=(90, 160, 75), width=2)

    elif shape_type == "palmate": # Grape
        cx, cy = 300, 300
        for i in range(num_pts):
            angle = (2 * math.pi * i) / num_pts
            r = 180 + 35 * math.cos(5 * angle)
            x = cx + r * math.sin(angle)
            y = cy + r * math.cos(angle)
            points.append((x, y))
        draw.polygon(points, fill=leaf_color, outline=(25, 80, 30))
        for deg in [0, 60, 120, 180, 240, 300]:
            rad = math.radians(deg)
            draw.line([(cx, cy), (cx + 140 * math.sin(rad), cy + 140 * math.cos(rad))], fill=(75, 165, 70), width=3)

    return img

# --- GOOD LEAVES ---
def make_good_leaves():
    # 1. Tomato Healthy
    img = draw_leaf_base(leaf_color=(46, 135, 55), shape_type="oval")
    save_to_both(img.filter(ImageFilter.SMOOTH), "good_leaves", "tomato_healthy.jpg")

    # 2. Potato Healthy
    img = draw_leaf_base(leaf_color=(40, 120, 48), shape_type="oval")
    save_to_both(img.filter(ImageFilter.SMOOTH), "good_leaves", "potato_healthy.jpg")

    # 3. Corn Healthy
    img = draw_leaf_base(leaf_color=(60, 145, 50), shape_type="long")
    save_to_both(img.filter(ImageFilter.SMOOTH), "good_leaves", "corn_healthy.jpg")

    # 4. Bell Pepper Healthy
    img = draw_leaf_base(leaf_color=(35, 115, 45), shape_type="oval")
    save_to_both(img.filter(ImageFilter.SMOOTH), "good_leaves", "bell_pepper_healthy.jpg")

    # 5. Grape Healthy
    img = draw_leaf_base(leaf_color=(50, 130, 50), shape_type="palmate")
    save_to_both(img.filter(ImageFilter.SMOOTH), "good_leaves", "grape_healthy.jpg")

    # 6. Apple Healthy
    img = draw_leaf_base(leaf_color=(45, 125, 52), shape_type="oval")
    save_to_both(img.filter(ImageFilter.SMOOTH), "good_leaves", "apple_healthy.jpg")

# --- BAD (DISEASED) LEAVES ---
def make_bad_leaves():
    # 1. Tomato Early Blight (Target spots)
    img = draw_leaf_base(leaf_color=(46, 120, 50), shape_type="oval")
    draw = ImageDraw.Draw(img)
    for lx, ly, rad in [(250, 260, 38), (340, 220, 30), (280, 360, 34), (350, 330, 24)]:
        draw.ellipse([lx - rad - 8, ly - rad - 8, lx + rad + 8, ly + rad + 8], fill=(195, 195, 30))
        draw.ellipse([lx - rad, ly - rad, lx + rad, ly + rad], fill=(55, 30, 15))
        draw.ellipse([lx - rad + 8, ly - rad + 8, lx + rad - 8, ly + rad - 8], fill=(95, 55, 25))
        draw.ellipse([lx - rad + 16, ly - rad + 16, lx + rad - 16, ly + rad - 16], fill=(40, 20, 10))
    save_to_both(img.filter(ImageFilter.SMOOTH_MORE), "bad_leaves", "tomato_early_blight.jpg")

    # 2. Tomato Late Blight (Water-soaked dark rot)
    img = draw_leaf_base(leaf_color=(46, 120, 50), shape_type="oval")
    draw = ImageDraw.Draw(img)
    for bx, by, rx, ry in [(230, 180, 60, 45), (320, 300, 75, 55), (250, 380, 50, 40)]:
        draw.ellipse([bx - rx, by - ry, bx + rx, by + ry], fill=(30, 40, 25))
        draw.ellipse([bx - rx + 10, by - ry + 10, bx + rx - 10, by + ry - 10], fill=(20, 25, 18))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "tomato_late_blight.jpg")

    # 3. Tomato Yellow Leaf Curl Virus (Chlorosis & curling)
    img = draw_leaf_base(leaf_color=(165, 185, 40), shape_type="oval")
    draw = ImageDraw.Draw(img)
    draw.polygon([(260, 180), (340, 190), (320, 280), (270, 270)], fill=(215, 215, 60))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "tomato_yellow_leaf_curl.jpg")

    # 4. Potato Early Blight
    img = draw_leaf_base(leaf_color=(42, 115, 45), shape_type="oval")
    draw = ImageDraw.Draw(img)
    for px, py in [(260, 230), (330, 280), (270, 340), (320, 190)]:
        draw.ellipse([px - 24, py - 24, px + 24, py + 24], fill=(180, 165, 35))
        draw.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(70, 40, 20))
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(40, 20, 10))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "potato_early_blight.jpg")

    # 5. Potato Late Blight
    img = draw_leaf_base(leaf_color=(42, 115, 45), shape_type="oval")
    draw = ImageDraw.Draw(img)
    draw.ellipse([210, 160, 350, 290], fill=(35, 45, 30))
    draw.ellipse([240, 310, 360, 420], fill=(25, 35, 20))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "potato_late_blight.jpg")

    # 6. Corn Common Rust
    img = draw_leaf_base(leaf_color=(75, 140, 60), shape_type="long")
    draw = ImageDraw.Draw(img)
    rng = np.random.RandomState(42)
    for _ in range(80):
        rx = int(rng.uniform(220, 380))
        ry = int(rng.uniform(90, 510))
        draw.ellipse([rx - 4, ry - 7, rx + 4, ry + 7], fill=(185, 65, 20))
        draw.ellipse([rx - 2, ry - 4, rx + 2, ry + 4], fill=(225, 100, 30))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "corn_common_rust.jpg")

    # 7. Bell Pepper Bacterial Spot
    img = draw_leaf_base(leaf_color=(38, 118, 48), shape_type="oval")
    draw = ImageDraw.Draw(img)
    rng = np.random.RandomState(99)
    for _ in range(60):
        bx = int(rng.uniform(230, 370))
        by = int(rng.uniform(180, 430))
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(130, 145, 45))
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(45, 35, 25))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "bell_pepper_bacterial_spot.jpg")

    # 8. Apple Scab (Velvety dark scabs)
    img = draw_leaf_base(leaf_color=(45, 125, 52), shape_type="oval")
    draw = ImageDraw.Draw(img)
    for sx, sy in [(260, 210), (330, 270), (280, 350)]:
        draw.ellipse([sx - 28, sy - 28, sx + 28, sy + 28], fill=(45, 60, 40))
        draw.ellipse([sx - 18, sy - 18, sx + 18, sy + 18], fill=(20, 25, 20))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "apple_scab.jpg")

    # 9. Grape Black Rot
    img = draw_leaf_base(leaf_color=(50, 130, 50), shape_type="palmate")
    draw = ImageDraw.Draw(img)
    for gx, gy in [(280, 220), (340, 320), (240, 350)]:
        draw.ellipse([gx - 26, gy - 26, gx + 26, gy + 26], fill=(85, 40, 25))
        draw.ellipse([gx - 18, gy - 18, gx + 18, gy + 18], fill=(35, 20, 15))
    save_to_both(img.filter(ImageFilter.SMOOTH), "bad_leaves", "grape_black_rot.jpg")

def main():
    print("=" * 60)
    print("ORGANIZING DATASET FOLDERS: good_leaves & bad_leaves")
    print("=" * 60)
    make_dirs()
    make_good_leaves()
    make_bad_leaves()
    print("=" * 60)
    print("SUCCESS: Both good_leaves and bad_leaves folders populated!")

if __name__ == "__main__":
    main()

