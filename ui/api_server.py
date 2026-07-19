"""
Flask API server for ContentPulse.
Serves the dashboard and provides JSON APIs for analysis and scoring.
"""

import json
import logging
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from config import ASSETS_DIR, LOGS_DIR, TOPICS, FORMATS, AUDIENCE_SEGMENTS
from orchestrator import run_pipeline, score_draft

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "api_server.log"))
logger.setLevel(logging.INFO)

# Initialize Flask app
app = Flask(__name__, static_folder=Path(__file__).parent, template_folder=Path(__file__).parent)
CORS(app)

logger.info("ContentPulse API Server initialized")


# ==================== STATIC & CONFIG ENDPOINTS ====================


@app.route("/")
def index():
    """Serve dashboard."""
    return render_template("index.html")


@app.route("/api/topics", methods=["GET"])
def get_topics():
    """Get list of topics."""
    return jsonify(TOPICS)


@app.route("/api/formats", methods=["GET"])
def get_formats():
    """Get list of formats."""
    return jsonify(FORMATS)


@app.route("/api/audiences", methods=["GET"])
def get_audiences():
    """Get list of audience segments."""
    return jsonify(AUDIENCE_SEGMENTS)


# ==================== ANALYSIS ENDPOINTS ====================


@app.route("/api/report", methods=["POST"])
def api_report():
    """Run full analysis pipeline and return report."""
    try:
        logger.info("Report request received")
        result = run_pipeline()
        logger.info("Report generated successfully")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/score", methods=["POST"])
def api_score():
    """Score a draft piece of content."""
    try:
        data = request.get_json()
        logger.info(f"Score request: {data.get('title')}")

        # Validate required fields
        required = ["title", "topic", "format", "audience_segment", "word_count"]
        missing = [f for f in required if f not in data]
        if missing:
            logger.warning(f"Missing fields: {missing}")
            return (
                jsonify({"error": f"Missing required fields: {', '.join(missing)}"}),
                400,
            )

        # Call scorer
        result = score_draft(
            title=data["title"],
            topic=data["topic"],
            fmt=data["format"],
            audience_segment=data["audience_segment"],
            word_count=int(data["word_count"]),
        )
        logger.info(
            f"Score computed: {result['prediction']['predicted_score']}"
        )
        return jsonify(result)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Scoring failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    logger.info("Starting ContentPulse API Server on 0.0.0.0:5050")
    app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)
