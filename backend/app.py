import logging
import time

from flask import Flask, request, jsonify, g, make_response
from flask_cors import CORS

from config import Config
from chatbot_engine import get_engine
from chat_html import CHAT_HTML

logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=Config.CORS_ORIGINS)

    with app.app_context():
        get_engine()

    @app.before_request
    def start_timer():
        g.start = time.perf_counter()

    @app.after_request
    def log_request(response):
        duration_ms = (time.perf_counter() - g.start) * 1000
        logger.info("%s %s -> %d (%.1f ms)", request.method, request.path, response.status_code, duration_ms)
        return response

    @app.route("/", methods=["GET"])
    def index():
        resp = make_response(CHAT_HTML)
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
        return resp

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json(silent=True)
        if not data or "message" not in data:
            return jsonify({"error": "Request body must be JSON with a 'message' field."}), 400
        user_input: str = data["message"].strip()
        if not user_input:
            return jsonify({"error": "Message cannot be empty."}), 400
        if len(user_input) > Config.MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"Message exceeds {Config.MAX_MESSAGE_LENGTH} characters."}), 400
        reply = get_engine().get_best_answer(user_input)
        return jsonify({"reply": reply})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/suggestions", methods=["GET"])
    def suggestions():
        samples = [
            "How to get certificate",
            "Reset my password",
            "Payment failed",
            "Enroll in a course",
            "Contact support"
        ]
        return jsonify({"suggestions": samples})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Unhandled exception: %s", e)
        return jsonify({"error": "An internal server error occurred."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT, host="0.0.0.0")
