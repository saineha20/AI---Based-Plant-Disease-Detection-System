# scripts/generate_sample_leaves.py
"""
Generates realistic sample leaf photographs for testing Kisan Mitra.
Stores sample images in data/sample_images/
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DIR = os.path.join(BASE_DIR, "data", "sample_images")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def create_leaf_base(width=600, height=600, bg_color=(235, 238, 235)):
    """Creates a neutral outdoor surface with realistic leaf mask and veins."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Leaf outline coordinates (lanceolate/ovate leaf)
    center_x, center_y = width // 2, height // 2
    points = []
    num_pts = 60
    for i in range(num_pts):
        angle = (2 * math.pi * i) / num_pts
        # Leaf contour equation
        r = 210 * (1.0 - 0.45 * math.cos(angle)) * math.sin(angle / 2.0)
        x = center_x + r * math.sin(angle)
        y = center_y + r * math.cos(angle) * 1.3 - 20
        points.append((x, y))

    # Base green leaf blade
    leaf_green = (46, 125, 50)
    draw.polygon(points, fill=leaf_green, outline=(30, 90, 35))

    # Add realistic main vein and secondary veins
    draw.line([(center_x, center_y - 200), (center_x, center_y + 190)], fill=(76, 175, 80), width=4)
    for v_y in range(center_y - 140, center_y + 140, 35):
        draw.line([(center_x, v_y), (center_x - 70, v_y - 25)], fill=(65, 155, 70), width=2)
        draw.line([(center_x, v_y), (center_x + 70, v_y - 25)], fill=(65, 155, 70), width=2)

    return img

def generate_tomato_early_blight():
    img = create_leaf_base()
    draw = ImageDraw.Draw(img)

    # Concentric early blight target lesions with yellow halos
    lesions = [(250, 270, 40), (330, 220, 32), (280, 370, 36), (360, 330, 25)]
    for lx, ly, rad in lesions:
        # Yellow chlorotic halo
        draw.ellipse([lx - rad - 8, ly - rad - 8, lx + rad + 8, ly + rad + 8], fill=(190, 195, 30))
        # Outer dark brown ring
        draw.ellipse([lx - rad, ly - rad, lx + rad, ly + rad], fill=(55, 30, 15))
        # Inner lighter ring
        draw.ellipse([lx - rad + 8, ly - rad + 8, lx + rad - 8, ly + rad - 8], fill=(95, 55, 25))
        # Bullseye center
        draw.ellipse([lx - rad + 16, ly - rad + 16, lx + rad - 16, ly + rad - 16], fill=(40, 20, 10))

    img = img.filter(ImageFilter.SMOOTH_MORE)
    path = os.path.join(SAMPLE_DIR, "tomato_early_blight.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"Generated: {path}")

def generate_tomato_healthy():
    img = create_leaf_base()
    draw = ImageDraw.Draw(img)
    # Bright healthy highlights
    draw.ellipse([270, 250, 330, 310], fill=(60, 150, 60))
    img = img.filter(ImageFilter.SMOOTH)
    path = os.path.join(SAMPLE_DIR, "tomato_healthy.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"Generated: {path}")

def generate_potato_early_blight():
    img = create_leaf_base(bg_color=(230, 230, 225))
    draw = ImageDraw.Draw(img)
    # Brown necrotic spots
    for px, py in [(260, 240), (340, 290), (270, 340), (320, 200)]:
        draw.ellipse([px - 22, py - 22, px + 22, py + 22], fill=(175, 160, 40))
        draw.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(70, 38, 20))
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(45, 25, 15))
    path = os.path.join(SAMPLE_DIR, "potato_early_blight.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"Generated: {path}")

def generate_corn_common_rust():
    img = Image.new("RGB", (600, 600), (240, 240, 235))
    draw = ImageDraw.Draw(img)
    # Elongated maize leaf blade
    draw.polygon([(180, 50), (420, 50), (380, 550), (220, 550)], fill=(75, 140, 60))
    draw.line([(300, 50), (300, 550)], fill=(120, 185, 100), width=6)
    # Cinnamon rust pustules
    rng = np.random.RandomState(42)
    for _ in range(75):
        rx = int(rng.uniform(220, 380))
        ry = int(rng.uniform(100, 500))
        draw.ellipse([rx - 4, ry - 8, rx + 4, ry + 8], fill=(180, 65, 25))
        draw.ellipse([rx - 2, ry - 5, rx + 2, ry + 5], fill=(215, 95, 30))
    path = os.path.join(SAMPLE_DIR, "corn_common_rust.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"Generated: {path}")

def generate_bell_pepper_bacterial_spot():
    img = create_leaf_base()
    draw = ImageDraw.Draw(img)
    # Small water-soaked angular bacterial spots
    rng = np.random.RandomState(99)
    for _ in range(50):
        bx = int(rng.uniform(230, 370))
        by = int(rng.uniform(200, 420))
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(130, 145, 45))
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(45, 35, 25))
    path = os.path.join(SAMPLE_DIR, "bell_pepper_bacterial_spot.jpg")
    img.save(path, "JPEG", quality=92)
    print(f"Generated: {path}")

def main():
    print("=" * 60)
    print("Generating Sample Leaf Images in data/sample_images/")
    print("=" * 60)
    generate_tomato_early_blight()
    generate_tomato_healthy()
    generate_potato_early_blight()
    generate_corn_common_rust()
    generate_bell_pepper_bacterial_spot()
    print("All sample leaf images ready for testing!")

if __name__ == "__main__":
    main()

