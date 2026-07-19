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
from werkzeug.utils import secure_filename
import csv


logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler(LOGS_DIR / "api_server.log"))
logger.setLevel(logging.INFO)

# Initialize Flask app
app = Flask(__name__, static_folder=Path(__file__).parent, template_folder=Path(__file__).parent)

# ==================== FILE UPLOAD CONFIGURATION ====================

UPLOAD_FOLDER = ASSETS_DIR / "user_uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size

ALLOWED_CSV_EXTENSIONS = {"csv"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "webm"}
ALLOWED_ASSET_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

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

        # Extract optional draft_markdown and asset_path
        draft_markdown = data.get("draft_markdown", None)
        asset_path = data.get("asset_path", None)

        # Call scorer
        result = score_draft(
            title=data["title"],
            topic=data["topic"],
            fmt=data["format"],
            audience_segment=data["audience_segment"],
            word_count=int(data["word_count"]),
            draft_markdown=draft_markdown,
            asset_path=asset_path,
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

# ==================== FILE UPLOAD ENDPOINTS ====================


@app.route("/api/upload-csv", methods=["POST"])
def upload_user_csv():
    """Upload custom company content CSV for personalized analysis."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename, ALLOWED_CSV_EXTENSIONS):
            return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400
        
        filename = secure_filename(file.filename)
        save_path = UPLOAD_FOLDER / filename
        file.save(str(save_path))
        
        logger.info(f"CSV uploaded: {filename}")
        
        # Validate CSV structure
        try:
            with open(save_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    return jsonify({"error": "CSV file is empty"}), 400
            
            logger.info(f"CSV validation passed: {len(rows)} rows")
        except Exception as e:
            logger.error(f"CSV validation failed: {e}")
            return jsonify({"error": f"Invalid CSV format: {str(e)}"}), 400
        
        # Run pipeline with custom dataset
        try:
            from orchestrator import run_pipeline
            result = run_pipeline(data_path=str(save_path))
            logger.info(f"Custom analysis completed: {filename}")
            return jsonify({
                "message": "Custom dataset processed successfully",
                "filename": filename,
                "rows_processed": len(rows),
                "result": result
            })
        except Exception as e:
            logger.error(f"Pipeline failed with custom data: {e}")
            return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"CSV upload error: {e}", exc_info=True)
        return jsonify({"error": "File upload failed"}), 500


@app.route("/api/upload-asset", methods=["POST"])
def upload_draft_asset():
    """Upload screenshot/video asset for multimodal draft scoring."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No asset uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename, ALLOWED_ASSET_EXTENSIONS):
            return jsonify({
                "error": f"Invalid file format. Allowed: {', '.join(ALLOWED_ASSET_EXTENSIONS)}"
            }), 400
        
        filename = secure_filename(file.filename)
        save_path = UPLOAD_FOLDER / filename
        file.save(str(save_path))
        
        logger.info(f"Asset uploaded: {filename}")
        
        # Determine asset type
        ext = filename.rsplit(".", 1)[1].lower()
        asset_type = "image" if ext in ALLOWED_IMAGE_EXTENSIONS else "video"
        
        return jsonify({
            "message": "Asset uploaded successfully",
            "asset_path": f"/assets/user_uploads/{filename}",
            "asset_name": filename,
            "asset_type": asset_type,
            "file_size": file.content_length
        })
    
    except Exception as e:
        logger.error(f"Asset upload error: {e}", exc_info=True)
        return jsonify({"error": "Asset upload failed"}), 500


@app.route("/api/score", methods=["POST"])
def api_score_with_asset():
    """Score a draft piece of content with optional multimodal asset."""
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

        # Extract optional fields
        draft_markdown = data.get("draft_markdown", None)
        asset_path = data.get("asset_path", None)

        # Call scorer with asset
        result = score_draft(
            title=data["title"],
            topic=data["topic"],
            fmt=data["format"],
            audience_segment=data["audience_segment"],
            word_count=int(data["word_count"]),
            draft_markdown=draft_markdown,
            asset_path=asset_path,
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


        # Call scorer
        result = score_draft(
            title=data["title"],
            topic=data["topic"],
            fmt=data["format"],
            audience_segment=data["audience_segment"],
            word_count=int(data["word_count"]),
            draft_markdown=draft_markdown,
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


@app.route("/assets/user_uploads/<filename>", methods=["GET"])
def serve_uploaded_file(filename: str):
    """Serve uploaded user files (images, videos, etc.)."""
    from flask import send_from_directory
    try:
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        logger.error(f"File serve error: {e}")
        return jsonify({"error": "File not found"}), 404


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
