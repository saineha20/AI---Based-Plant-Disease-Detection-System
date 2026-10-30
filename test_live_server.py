# scripts/test_live_server.py
import urllib.request
import json
import uuid

def test_api(image_path, filename):
    boundary = uuid.uuid4().hex
    with open(image_path, 'rb') as f:
        file_bytes = f.read()

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8') + file_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/analyze',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode())
    print(f"{filename:30} -> {data['prediction']['crop']} | {data['prediction']['disease_name']} ({data['prediction']['confidence_percentage']}%)")

print("Testing live Flask backend on http://127.0.0.1:5000/api/analyze:")
print("-" * 75)
test_api('data/potato_early_blight.jpg', 'potato_early_blight.jpg')
test_api('data/potato_late_blight.jpg', 'potato_late_blight.jpg')
test_api('data/potato_healthy.jpg', 'potato_healthy.jpg')
test_api('data/corn_common_rust.jpg', 'corn_common_rust.jpg')
test_api('data/apple_scab.jpg', 'apple_scab.jpg')
test_api('data/bell_pepper_bacterial_spot.jpg', 'bell_pepper_bacterial_spot.jpg')
test_api('data/grape_black_rot.jpg', 'grape_black_rot.jpg')

