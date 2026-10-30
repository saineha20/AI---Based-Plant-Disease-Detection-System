# app.py
"""
Kisan Mitra - AI-Powered Plant Leaf Disease Detection & Treatment Assistant
Main Flask Application Server
"""
import os
import sys
import logging

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger("kisan_mitra")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
    app.config['UPLOAD_FOLDER'] = UPLOADS_DIR

    # Enable Cross-Origin Resource Sharing
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API routes
    from backend.routes import api_bp
    app.register_blueprint(api_bp)

    # Serve Frontend UI
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(FRONTEND_DIR, path)):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, 'index.html')

    # Error Handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "status": "error",
            "error_type": "file_too_large",
            "message": "File size exceeds the 10 MB limit. Please upload a smaller compressed image."
        }), 413

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "error_type": "not_found",
            "message": "Requested endpoint does not exist."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "status": "error",
            "error_type": "internal_server_error",
            "message": "An internal error occurred on the server."
        }), 500

    return app

if __name__ == '__main__':
    import webbrowser
    import threading

    app = create_app()
    desired_port = int(os.environ.get("PORT", 5000))
    candidate_ports = [desired_port, 8080, 8000, 5050]
    # Remove duplicates preserving order
    candidate_ports = list(dict.fromkeys(candidate_ports))

    started = False
    for p in candidate_ports:
        try:
            print("=" * 65)
            print("[KISAN MITRA] AI Plant Leaf Disease Detection Assistant")
            print(f"Backend & UI running at: http://localhost:{p}/")
            print(f"Also reachable at:      http://127.0.0.1:{p}/")
            print("=" * 65)

            # Auto-open browser in 1.2 seconds once server is ready
            threading.Timer(1.2, lambda port=p: webbrowser.open(f"http://localhost:{port}/")).start()

            app.run(host='0.0.0.0', port=p, debug=False)
            started = True
            break
        except OSError as err:
            print(f"[Notice] Port {p} could not be bound ({err}). Trying alternative port...")

    if not started:
        print("[Error] Could not find an open network port. Please close conflicting applications.")

