# backend/routes.py
"""
Flask REST API routes for Kisan Mitra Plant Disease Assistant.
"""
import os
import io
import base64
import logging
from flask import Blueprint, request, jsonify, current_app

from backend.validators import validate_image_file, ValidationError
from backend.image_processor import LeafImageProcessor, ImageProcessingError
from backend.disease_detector import detector, ModelInferenceError
from backend.treatment_service import treatment_service
from backend.translation_service import translation_service
from backend.voice_service import voice_service
from backend.database import (
    save_diagnosis_to_db,
    get_diagnosis_history_from_db,
    clear_diagnosis_history_db,
    save_farmer_feedback_db
)

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')
processor = LeafImageProcessor()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Returns backend status, loaded model state, and runtime environment info."""
    model_status = detector.get_model_status()
    return jsonify({
        "status": "healthy",
        "app_name": "Kisan Mitra - AI Plant Disease Assistant",
        "version": "1.0.0",
        "languages": ["en", "hi", "te"],
        "model": model_status
    }), 200

@api_bp.route('/model-info', methods=['GET'])
def model_info():
    """Returns detailed information about the active AI inference engine and classes."""
    return jsonify({
        "model_status": detector.get_model_status(),
        "classes": detector.classes,
        "classes_count": len(detector.classes)
    }), 200

@api_bp.route('/analyze', methods=['POST'])
def analyze_leaf():
    """
    Accepts an uploaded leaf photo, validates clarity/format,
    runs genuine AI classification, and returns localized agricultural advisory.
    """
    lang = request.form.get("lang", "en").lower().strip()
    if lang not in ["en", "hi", "te"]:
        lang = "en"

    # 1. Retrieve uploaded file
    file_obj = None
    if 'image' in request.files:
        file_obj = request.files['image']
    elif 'file' in request.files:
        file_obj = request.files['file']

    if not file_obj or file_obj.filename == '':
        return jsonify({
            "status": "error",
            "error_type": "missing_file",
            "message": translation_service.get_text("choose_file", lang=lang) + " is required."
        }), 400

    # 2. File size and header validation
    try:
        val_res = validate_image_file(file_obj)
    except ValidationError as e:
        return jsonify({
            "status": "error",
            "error_type": "validation_failed",
            "message": str(e)
        }), 400

    # 3. Image decoding & quality evaluation
    try:
        img = processor.load_image(file_obj.stream)
        quality = processor.assess_quality(img)
    except ImageProcessingError as e:
        return jsonify({
            "status": "error",
            "error_type": "corrupted_image",
            "message": str(e)
        }), 422
    except Exception as e:
        logger.error(f"Error loading image: {e}")
        return jsonify({
            "status": "error",
            "error_type": "image_read_error",
            "message": "Unable to process this image file. Please upload a clear photo."
        }), 400

    # 4. Check if model is ready
    model_status = detector.get_model_status()
    if not model_status["model_loaded"]:
        return jsonify({
            "status": "error",
            "error_type": "model_not_loaded",
            "message": (
                "AI disease classification model is not loaded. "
                "Please run 'python scripts/setup_model.py' to initialize the model."
            ),
            "quality": quality
        }), 503

    # 5. Tensor Preprocessing & Inference
    try:
        layout = "NCHW" if detector.model_backend in ["onnx", "pytorch"] else "NHWC"
        input_tensor = processor.preprocess_tensor(img, layout=layout)
        prediction = detector.predict(input_tensor, filename=file_obj.filename, pil_img=img)
    except ModelInferenceError as e:
        return jsonify({
            "status": "error",
            "error_type": "inference_failure",
            "message": str(e)
        }), 500
    except Exception as e:
        logger.error(f"Inference exception: {e}")
        return jsonify({
            "status": "error",
            "error_type": "server_inference_error",
            "message": "Unexpected error during AI model forward pass."
        }), 500

    # 6. Build localized report
    report = treatment_service.build_analysis_report(
        prediction=prediction,
        quality=quality,
        lang=lang
    )

    # 7. Generate lightweight thumbnail for History card display
    thumb_b64 = None
    try:
        thumb_copy = image.copy().convert("RGB")
        thumb_copy.thumbnail((160, 160))
        buf = io.BytesIO()
        thumb_copy.save(buf, format="JPEG", quality=80)
        thumb_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception as t_err:
        logger.warning(f"Thumbnail generation error: {t_err}")

    # 8. Persist to SQLite Database
    try:
        record_id = save_diagnosis_to_db({
            "disease_id": prediction["top_prediction"]["class_id"],
            "crop": report["prediction"]["crop"],
            "disease_name": report["prediction"]["disease_name"],
            "confidence": report["prediction"]["confidence_percentage"],
            "confidence_rating": report["prediction"]["confidence_rating"],
            "diagnosis_status": report["prediction"]["diagnosis_status"],
            "language": lang,
            "thumbnail": thumb_b64 or "",
            "quality_metrics": quality.get("metrics", {})
        })
        report["record_id"] = record_id
    except Exception as db_err:
        logger.warning(f"Could not persist record to SQLite: {db_err}")

    return jsonify(report), 200

@api_bp.route('/diseases', methods=['GET'])
def list_diseases():
    """Returns catalog of all supported crop disease conditions."""
    lang = request.args.get('lang', 'en').lower()
    diseases = treatment_service.get_supported_diseases_list(lang=lang)
    return jsonify({
        "status": "success",
        "total": len(diseases),
        "language": lang,
        "diseases": diseases
    }), 200

@api_bp.route('/treatment/<disease_id>', methods=['GET'])
def get_treatment(disease_id):
    """Returns verified treatment recommendations for a disease ID."""
    lang = request.args.get('lang', 'en').lower()
    disease_info = treatment_service.get_disease_info(disease_id, lang=lang)
    treatment_info = treatment_service.get_treatment_info(disease_id, lang=lang)

    if not disease_info or not treatment_info:
        return jsonify({
            "status": "error",
            "message": f"Disease '{disease_id}' not found in agricultural knowledge database."
        }), 404

    return jsonify({
        "status": "success",
        "language": lang,
        "disease_info": disease_info,
        "treatment": treatment_info
    }), 200

@api_bp.route('/translations/<lang>', methods=['GET'])
def get_translations(lang):
    """Returns UI translation strings for a requested language."""
    strings = translation_service.get_translations_for_lang(lang=lang)
    return jsonify({
        "status": "success",
        "language": lang,
        "translations": strings
    }), 200

@api_bp.route('/voice/query', methods=['POST'])
def handle_voice_query():
    """Accepts spoken question text and contextual diagnosis, returns spoken response."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    context = data.get("context", {})
    lang = data.get("lang", "en").lower()

    res = voice_service.answer_query(query=query, context=context, lang=lang)
    return jsonify({
        "status": "success",
        "language": lang,
        "result": res
    }), 200

@api_bp.route('/history', methods=['GET'])
def get_history():
    """Retrieves recent diagnosis history records from the SQLite database."""
    limit = request.args.get('limit', 20, type=int)
    history = get_diagnosis_history_from_db(limit=limit)
    return jsonify({
        "status": "success",
        "count": len(history),
        "history": history
    }), 200

@api_bp.route('/history', methods=['DELETE'])
def clear_history():
    """Clears all diagnosis history records from the SQLite database."""
    clear_diagnosis_history_db()
    return jsonify({
        "status": "success",
        "message": "Diagnosis history database cleared."
    }), 200

@api_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Accepts farmer feedback regarding diagnostic accuracy and field outcomes."""
    data = request.get_json(silent=True) or {}
    record_id = data.get("record_id")
    is_accurate = data.get("is_accurate", True)
    comments = data.get("comments", "")

    feedback_id = save_farmer_feedback_db(
        diagnosis_id=record_id,
        is_accurate=is_accurate,
        comments=comments
    )
    return jsonify({
        "status": "success",
        "feedback_id": feedback_id,
        "message": "Farmer feedback recorded successfully in database."
    }), 201

