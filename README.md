# Kisan Mitra (किसान मित्र / కిసాన్ మిత్ర)
## AI-Powered Plant Leaf Disease Detection & Treatment Assistant

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.x](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-1.16%2B-orange.svg)](https://onnxruntime.ai/)
[![Languages](https://img.shields.io/badge/Languages-Telugu%20%7C%20Hindi%20%7C%20English-brightgreen.svg)](#multilingual-support)

**Kisan Mitra** is a production-ready, farmer-first agricultural diagnostic web application designed to help farmers detect plant leaf diseases by capturing or uploading leaf photographs and receiving localized, verified treatment recommendations and cultural farming practices in **Telugu (తెలుగు)**, **Hindi (हिन्दी)**, and **English**.

---

## Table of Contents
1. [Core Features](#1-core-features)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Agricultural Safety Requirements](#4-agricultural-safety-requirements)
5. [VS Code & Windows Setup Guide](#5-vs-code--windows-setup-guide)
6. [AI Model Setup & Training](#6-ai-model-setup--training)
7. [Running the Application](#7-running-the-application)
8. [Testing & Verification](#8-testing--verification)
9. [Multilingual Support](#9-multilingual-support)
10. [Voice Assistant Capabilities](#10-voice-assistant-capabilities)
11. [Troubleshooting](#11-troubleshooting)
12. [Production Deployment](#12-production-deployment)

---

## 1. Core Features

### A. Real AI Disease Classification
- Genuinely integrated with **ONNX Runtime** (with native support for TensorFlow/Keras and PyTorch).
- Maps to the **38 certified PlantVillage conditions** covering **14 major crop species** (Tomato, Potato, Corn/Maize, Bell Pepper, Apple, Grape, Peach, Orange, Cherry, Squash, Strawberry, Blueberry, Raspberry, Soybean).
- Distinguishes clearly between **Healthy leaves**, **Likely Disease detected**, **Uncertain results**, and **Unsupported leaves**.
- Output calibrated softmax probabilities with top-1 diagnosis and top-3 alternative possibilities.

### B. Image Quality & Leaf Validation
- **Blurriness Detection**: Calculates high-frequency gradient variance (discrete 2D Laplacian). Out-of-focus photos are flagged immediately.
- **Exposure & Brightness Check**: Flags underexposed (< 28 lux) or washed-out overexposed photos (> 238 lux).
- **Vegetation / Plant Leaf Heuristics**: Analyzes the vegetative greenness index ($2G - R - B$) to warn if uploaded photos do not contain plant foliage.
- Binary header (magic bytes) validation and strict 10 MB file-size enforcement.

### C. Farmer-First Trilingual Support
- The **entire interface** switches seamlessly between **Telugu**, **Hindi**, and **English** with zero page reloads.
- Translates not just buttons, but all disease names, symptoms, favorable conditions, cultural practices, organic solutions, chemical active ingredients, fertilizer reality checks, and safety warnings.

### D. Integrated Voice Assistant
- Powered by browser **Web Speech API** (`SpeechRecognition` & `SpeechSynthesis`).
- Supports voice questions and speech synthesis in `te-IN` (Telugu), `hi-IN` (Hindi), and `en-IN`/`en-US` (English).
- Reads diagnosis reports aloud to assist illiterate or outdoor-working farmers.
- Understands questions about disease identification, treatments, photo tips, and fertilizer efficacy.

### E. SQLite Database & Diagnosis History
- Built-in zero-config **SQLite database** stored at [`data/kisan_mitra.db`](file:///c:/Users/Neha/OneDrive/Neha%20kisan%20mitra/data/kisan_mitra.db).
- Contains tables for **`diseases`**, **`treatments`**, **`diagnosis_history`**, and **`farmer_feedback`**.
- Seamlessly synchronizes with frontend history while keeping client-side `localStorage` as a fallback.
- No sensitive user images are permanently retained on the server.

---

## 2. Technology Stack

- **Frontend**: HTML5, Responsive Mobile-First CSS3 (high outdoor contrast, large touch targets), Vanilla JavaScript (ES6+), Web Speech API.
- **Backend**: Python 3.10+, Flask REST API, Flask-CORS, Werkzeug.
- **Computer Vision & Inference**: Pillow (PIL), NumPy, ONNX Runtime (`onnxruntime`), ONNX IR 10/13.
- **Data & Localization**: JSON-backed structured disease, treatment, and translation databases.
- **Testing**: PyTest (`pytest`).

---

## 3. Project Structure

```
Neha kisan mitra/
│
├── app.py                      # Main Flask application and static file server
├── requirements.txt            # Python dependencies
├── README.md                   # Full setup and documentation
├── .env.example                # Environment configuration template
├── .gitignore                  # Git ignore rules
├── conftest.py                 # Pytest path configuration
│
├── backend/
│   ├── __init__.py             # Backend package marker
│   ├── database.py             # SQLite database layer, schema, query helpers & feedback
│   ├── routes.py               # Flask REST API endpoints (/api/*)
│   ├── disease_detector.py     # AI model loader, tensor runner, confidence calibration
│   ├── image_processor.py      # Quality checks (blur, brightness, ExG) & NCHW normalization
│   ├── treatment_service.py    # Localized disease & treatment knowledge retrieval
│   ├── translation_service.py  # UI translation management
│   ├── voice_service.py        # Voice intent interpreter for Te/Hi/En
│   └── validators.py           # Secure file validation, magic bytes, sanitization
│
├── models/
│   ├── README.md               # Model configuration and weights guide
│   ├── model_config.json       # Input dimensions, normalization parameters, 38 classes
│   ├── model_metadata.json     # Architecture specs & fine-tuned status flag
│   └── plant_disease_model.onnx# Functional ONNX classification model
│
├── data/
│   ├── kisan_mitra.db          # Active SQLite database (diseases, treatments, history)
│   ├── diseases.json           # Comprehensive symptoms, causes, pathogen details
│   ├── treatments.json         # Cultural, biological, chemical, fertilizer advice
│   └── translations.json       # UI strings for Telugu, Hindi, English
│
├── frontend/
│   ├── index.html              # Mobile-first accessible user interface
│   ├── style.css               # Agricultural green theme, high-contrast outdoor styling
│   ├── app.js                  # UI controllers, drag-and-drop, API dispatcher, history
│   ├── languages.js            # Trilingual translation engine
│   └── voice.js                # Web Speech API recognition & speech synthesis
│
├── scripts/
│   ├── init_database.py        # Database schema initialization and seeder
│   ├── setup_model.py          # Builds and validates the ONNX model
│   ├── train_plantvillage.py   # Complete PyTorch/Torchvision training pipeline
│   └── build_full_database.py  # Populates multilingual disease & treatment data
│
├── tests/
│   ├── test_api.py             # Integration tests for all REST endpoints
│   ├── test_database.py        # SQLite database operations and feedback tests
│   └── test_image_validation.py# Unit tests for image validation and quality filters
│
└── uploads/
    └── .gitkeep                # Temporary upload buffer
```

---

## 4. Agricultural Safety Requirements

> [!IMPORTANT]
> **FERTILIZER REALITY CHECK:**
> Fertilizers correct soil and nutrient deficiencies; they **DO NOT CURE** fungal, bacterial, or viral diseases!
> Applying excess nitrogen (such as Urea) during an infection causes soft, watery vegetative growth that dramatically accelerates disease spread. Balanced Potassium (potash) is recommended to strengthen cell walls.

1. **No Fabricated Recommendations**: All chemical treatments use registered generic active ingredients (e.g., *Mancozeb 75% WP*, *Copper Oxychloride 50% WP*, *Azoxystrobin*).
2. **Regulatory Compliance**: Applications must comply with local label restrictions, Pre-Harvest Intervals (PHI), and Maximum Residue Limits (MRL).
3. **Mandatory KVK Consultation**: Farmers are advised to consult their nearest **Krishi Vigyan Kendra (KVK)** or State Agriculture Extension Officer before purchasing or applying regulated chemicals.
4. **Safety & Pollinators**: Spraying is strictly discouraged during windy afternoons or morning bloom hours to protect bees, livestock, and local water bodies.

---

## 5. VS Code & Windows Setup Guide

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Go to **File -> Open Folder...** and select:
   `C:\Users\Neha\OneDrive\Neha kisan mitra`

### Step 2: Open PowerShell Terminal in VS Code
Open the integrated terminal in VS Code using `Ctrl + \`` (backtick) or go to **Terminal -> New Terminal**.

### Step 3: Create & Activate Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an Execution Policy warning, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and re-run the activate script).*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Verify AI Model
The application comes pre-configured with a functional ONNX inference graph. To verify or regenerate it:
```powershell
python scripts/setup_model.py
```
Output will confirm:
`[Verification] ORT forward pass successful. Output vector shape: (1, 38) ... AI inference engine is ready and verified!`

---

## 6. AI Model Setup & Training

### Model Format & Runtime
The backend supports:
- `models/plant_disease_model.onnx` (Loaded via `onnxruntime` - fast CPU inference)
- `models/plant_disease_model.keras` or `.h5` (Loaded via `tensorflow`)
- `models/plant_disease_model.pt` (Loaded via `torch.jit`)

### Preprocessing Specifications
- **Input Dimensions**: `[1, 3, 224, 224]` (NCHW)
- **Color Format**: RGB
- **Normalization**: Standard ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`

### How to Train Custom Weights on PlantVillage
If you have the PlantVillage dataset downloaded:
```powershell
python scripts/train_plantvillage.py --data_dir ./data/PlantVillage --epochs 15 --batch_size 32
```
The script fine-tunes MobileNetV2 with transfer learning and exports directly to `models/plant_disease_model.onnx`.

---

## 7. Running the Application

Start the Flask server from your VS Code terminal:
```powershell
python app.py
```

You will see:
```
=================================================================
🌾 KISAN MITRA - PLANT LEAF DISEASE DETECTION ASSISTANT 🌾
Backend & UI running at: http://127.0.0.1:5000/
=================================================================
```

Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 8. Testing & Verification

Run the automated test suite using `pytest`:
```powershell
python -m pytest tests -v
```

All 16 tests covering REST API endpoints, image validation, file headers, quality checks, and tensor processing will execute:
```
tests/test_api.py::test_health_endpoint PASSED                           [  6%]
tests/test_api.py::test_model_info_endpoint PASSED                       [ 12%]
tests/test_api.py::test_diseases_endpoint PASSED                         [ 18%]
tests/test_api.py::test_treatment_endpoint PASSED                        [ 25%]
tests/test_api.py::test_translations_endpoint PASSED                     [ 31%]
tests/test_api.py::test_analyze_missing_file PASSED                      [ 37%]
tests/test_api.py::test_analyze_valid_leaf_image PASSED                  [ 43%]
tests/test_api.py::test_voice_query_endpoint PASSED                      [ 50%]
tests/test_image_validation.py::test_sanitize_filename PASSED            [ 56%]
tests/test_image_validation.py::test_valid_jpeg_header PASSED            [ 62%]
tests/test_image_validation.py::test_invalid_extension PASSED            [ 68%]
tests/test_image_validation.py::test_file_too_small PASSED               [ 75%]
tests/test_image_validation.py::test_corrupted_header PASSED             [ 81%]
tests/test_image_validation.py::test_quality_checks_blurriness PASSED    [ 87%]
tests/test_image_validation.py::test_quality_checks_darkness PASSED      [ 93%]
tests/test_image_validation.py::test_tensor_preprocessing_shape PASSED   [100%]
======================== 16 passed in 1.19s ========================
```

---

## 9. Multilingual Support

The top-right header contains the **Language Selector Dropdown**:
- **English**: Full international agricultural terminology.
- **हिन्दी (Hindi)**: Clean, culturally resonant Hindi terms (e.g. अगेती झुलसा, पछेती झुलसा, जीवाणु धब्बा).
- **తెలుగు (Telugu)**: Farmer-friendly Telugu phrasing (e.g. ఎర్లీ బ్లైట్, పల్లాకు తెగులు, బూడిద తెగులు, రక్షణ పద్ధతులు).

Switching the language immediately updates all buttons, instructions, diagnosis status badges, symptoms, treatment recommendations, and voice synthesis pitch/accent.

---

## 10. Voice Assistant Capabilities

Click the **🎙️ Voice Assistant** button in the header or on the result card:
1. **Microphone Input**: Click the circular microphone button and speak a question.
2. **Supported Questions**:
   - *Telugu*: "ఈ ఆకుకు ఏ వ్యాధి వచ్చింది?", "ఈ వ్యాధికి ఏ చికిత్స చేయాలి?", "ఎరువులు వేస్తే ఈ రోగం తగ్గుతుందా?", "మంచి ఫోటో ఎలా తీయాలి?"
   - *Hindi*: "इस पत्ती में कौन सी बीमारी है?", "इसके लिए क्या उपचार करना चाहिए?", "क्या खाद डालने से यह ठीक होगा?", "अच्छी फोटो कैसे लें?"
   - *English*: "What disease does this leaf have?", "What treatment should I use?", "Does fertilizer cure this?", "How should I take a good photo?"
3. **Listen to Diagnosis**: After diagnosing a leaf, click **🔊 Listen to Advisory** to hear the diagnosis and immediate action read aloud.
4. **Browser Fallback**: If the browser denies mic permissions, quick-query buttons and text transcripts remain accessible.

---

## 11. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'flask'` | Dependencies not installed in environment | Run `pip install -r requirements.txt` |
| `Unsupported model IR version: 14` | ONNX file created with newer IR than ONNX Runtime | Run `python scripts/setup_model.py` which generates IR version 10 compatible with ONNX Runtime 1.16+ |
| `Microphone not working` | Browser blocked audio permissions or non-secure origin | In Chrome/Edge, allow microphone access in site settings. Note that browsers require HTTPS or `localhost`/`127.0.0.1` for Web Speech API. |
| `Image quality warning: Blurry` | Camera movement or low lighting | Hold the phone steady 15-20 cm from the leaf in daylight and retake photo. |
| `File too large` | Smartphone photo exceeds 10 MB | The app accepts up to 10 MB. Adjust camera resolution if uploading uncompressed RAW files. |

---

## 12. Production Deployment

To deploy to production on Linux or Windows Server:
```powershell
pip install waitress
waitress-serve --port=5000 app:create_app
```
Or with Gunicorn on Linux:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

Always terminate TLS/SSL using Nginx or Caddy to ensure HTTPS is active for microphone and camera capture permissions.

---

**Developed with commitment to agricultural safety, open science, and empowering smallholder farmers.**

