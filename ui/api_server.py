import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path
import io
import csv
from datetime import date, datetime
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import ContentPulse configurations and orchestrators
from config import DATA_PATH, TOPICS, FORMATS, AUDIENCE_SEGMENTS
from orchestrator import run_pipeline, score_draft

# Configure logging
logger = logging.getLogger("devpulse.api")
logger.setLevel(logging.INFO)

# Initialize Flask app
UI_PATH = Path(__file__).parent
app = Flask(__name__, static_folder=str(UI_PATH), template_folder=str(UI_PATH))
CORS(app)

# Active database of content performance entries
stored_data = []

def load_initial_data():
    """Load standard content data on startup to bootstrap stored_data."""
    global stored_data
    stored_data.clear()
    csv_file = Path(DATA_PATH)
    if csv_file.exists():
        try:
            with open(csv_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stored_data.append({
                        "title": row.get("title", "Untitled"),
                        "url": row.get("url", "https://example.com/content"),
                        "topic": row.get("topic", "API Design"),
                        "format": row.get("format", "technical_blog"),
                        "audience_segment": row.get("audience_segment", "developers"),
                        "word_count": int(row.get("word_count") or row.get("word_count", 1500)),
                        "publish_date": row.get("publish_date", date.today().isoformat()),
                        "views": int(row.get("views") or 0),
                        "engagement_rate": float(row.get("engagement_rate") or 0.05),
                        "avg_time_on_page": float(row.get("avg_time_on_page") or 120.0),
                        "conversions": int(row.get("conversions") or 0),
                        "search_rank": int(row.get("search_rank")) if row.get("search_rank") and row.get("search_rank").isdigit() else None,
                        "github_stars_growth": int(row.get("github_stars_growth") or 0),
                        # UI Compatibility Properties
                        "audience": row.get("audience_segment", "developers"),
                        "wordcount": int(row.get("word_count") or 1500),
                        "performance_score": float(row.get("performance_score") or 75.0)
                    })
            logger.info(f"Loaded {len(stored_data)} initial rows from {csv_file}")
        except Exception as e:
            logger.error(f"Failed to bootstrap data from CSV: {e}", exc_info=True)

# Bootstrap the active data on startup
load_initial_data()

def save_stored_data_to_temp_csv():
    """Save memory storage to a temporary file for Agent Ingestion."""
    temp_path = Path("data/temp_active_data.csv")
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "title", "url", "topic", "format", "audience_segment", "word_count",
            "publish_date", "views", "engagement_rate", "avg_time_on_page", "conversions", "search_rank", "github_stars_growth"
        ])
        writer.writeheader()
        for item in stored_data:
            writer.writerow({
                "title": item.get("title", "Untitled"),
                "url": item.get("url", "https://example.com/content"),
                "topic": item.get("topic", "API Design"),
                "format": item.get("format", "technical_blog"),
                "audience_segment": item.get("audience_segment") or item.get("audience") or "developers",
                "word_count": int(item.get("word_count") or item.get("wordcount") or 1500),
                "publish_date": item.get("publish_date") or date.today().isoformat(),
                "views": int(item.get("views") or 0),
                "engagement_rate": float(item.get("engagement_rate") or 0.05),
                "avg_time_on_page": float(item.get("avg_time_on_page") or 120.0),
                "conversions": int(item.get("conversions") or 0),
                "search_rank": item.get("search_rank") if item.get("search_rank") is not None else None,
                "github_stars_growth": int(item.get("github_stars_growth") or 0)
            })
    return str(temp_path)


# ==================== GENERAL ROUTES ====================

@app.route("/")
def index():
    """Serve main HTML dashboard."""
    with open(UI_PATH / "index.html", "r") as f:
        return f.read(), 200

@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files with appropriate content types."""
    file_path = UI_PATH / filename
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            if filename.endswith(".css"):
                return f.read(), 200, {"Content-Type": "text/css"}
            elif filename.endswith(".js"):
                return f.read(), 200, {"Content-Type": "application/javascript"}
            else:
                return f.read(), 200
    return "File not found", 200  # Return 200 per user rule: "end point should always be 200 for all of the buttons clicked"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "DevPulse is running"}), 200


# ==================== API ENDPOINTS (Always 200 OK) ====================

@app.route("/api/topics", methods=["GET"])
def get_topics():
    return jsonify(TOPICS), 200

@app.route("/api/formats", methods=["GET"])
def get_formats():
    return jsonify(FORMATS), 200

@app.route("/api/audiences", methods=["GET"])
def get_audiences():
    return jsonify(AUDIENCE_SEGMENTS), 200

@app.route("/api/data", methods=["GET"])
def get_data():
    try:
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)
        paginated = stored_data[offset:offset+limit]
        return jsonify({
            "success": True,
            "rows": paginated,
            "total": len(stored_data),
            "limit": limit,
            "offset": offset
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "rows": [], "total": 0}), 200

@app.route("/api/add-data", methods=["POST"])
def add_data():
    try:
        data = request.get_json()
        entry = {
            "title": data.get("title", "Untitled"),
            "url": data.get("url") or f"https://example.com/content-{len(stored_data)}",
            "topic": data.get("topic", "API Design"),
            "format": data.get("format", "technical_blog"),
            "audience_segment": data.get("audience") or data.get("audience_segment") or "developers",
            "word_count": int(data.get("wordcount") or data.get("word_count") or 1500),
            "publish_date": data.get("publish_date") or date.today().isoformat(),
            "views": int(data.get("views") or 0),
            "engagement_rate": float(data.get("engagement_rate") or 0.05),
            "avg_time_on_page": float(data.get("avg_time_on_page") or 120.0),
            "conversions": int(data.get("conversions") or 0),
            "search_rank": int(data.get("search_rank")) if data.get("search_rank") is not None else None,
            "github_stars_growth": int(data.get("github_stars_growth") or 0),
            # Keep frontend-facing values for compatibility:
            "audience": data.get("audience") or data.get("audience_segment") or "developers",
            "wordcount": int(data.get("wordcount") or data.get("word_count") or 1500),
            "performance_score": float(data.get("score") or 75.0)
        }
        stored_data.append(entry)
        return jsonify({
            "success": True,
            "message": f"Added: {entry['title']}",
            "entry": entry
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 200

@app.route("/api/score", methods=["POST"])
def score_content():
    """Calculate and return score with recommendations using Predictor Agent."""
    try:
        data = request.get_json()
        temp_csv = save_stored_data_to_temp_csv()
        
        result = score_draft(
            title=data.get("title", "Untitled"),
            topic=data.get("topic", "API Design"),
            fmt=data.get("format", "technical_blog"),
            audience_segment=data.get("audience") or data.get("audience_segment") or "developers",
            word_count=int(data.get("word_count") or data.get("wordcount") or 1500),
            data_path=temp_csv,
            draft_markdown=data.get("draft_markdown") or data.get("markdown") or ""
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "prediction": {
                "predicted_score": 50,
                "reasoning": f"Prediction failed due to exception: {e}",
                "suggestions": [
                    "Ensure topic and format are from standard collections.",
                    "Verify the content fields are not empty.",
                    "Check network and backend service logs."
                ]
            }
        }), 200

@app.route("/api/report", methods=["POST"])
def generate_report_api():
    """Triggers ContentPulse Pipeline on the live dataset."""
    try:
        temp_csv = save_stored_data_to_temp_csv()
        result = run_pipeline(data_path=temp_csv)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "report": {
                "summary": f"Failed to generate intelligence report dynamically: {e}",
                "continue_items": [],
                "stop_items": [],
                "create_next": []
            },
            "analysis": {
                "top_topics": [],
                "top_formats": [],
                "insights": ["Failed to load real insights.", "Verify dataset integrity."]
            }
        }), 200

@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    """Append uploaded CSV records to active stored_data."""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 200
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 200
        
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_data = csv.DictReader(stream)
        
        rows_processed = 0
        for row in csv_data:
            entry = {
                "title": row.get("title", "Untitled"),
                "url": row.get("url", "https://example.com/content"),
                "topic": row.get("topic", "API Design"),
                "format": row.get("format", "technical_blog"),
                "audience_segment": row.get("audience_segment", "developers"),
                "word_count": int(row.get("word_count") or row.get("word_count", 1500)),
                "publish_date": row.get("publish_date", date.today().isoformat()),
                "views": int(row.get("views") or 0),
                "engagement_rate": float(row.get("engagement_rate") or 0.05),
                "avg_time_on_page": float(row.get("avg_time_on_page") or 120.0),
                "conversions": int(row.get("conversions") or 0),
                "search_rank": int(row.get("search_rank")) if row.get("search_rank") and row.get("search_rank").isdigit() else None,
                "github_stars_growth": int(row.get("github_stars_growth") or 0),
                # Frontend compatible fields
                "audience": row.get("audience_segment", "developers"),
                "wordcount": int(row.get("word_count") or 1500),
                "performance_score": float(row.get("performance_score") or 75.0)
            }
            stored_data.append(entry)
            rows_processed += 1
        
        return jsonify({
            "success": True,
            "rows_processed": rows_processed,
            "message": f"Successfully parsed and loaded {rows_processed} rows."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 200

@app.route("/api/ab-test", methods=["POST"])
def ab_test():
    try:
        data = request.get_json()
        headlines = data.get("headlines", [])
        if not headlines:
            return jsonify({"success": False, "error": "No headlines provided"}), 200
        
        scores = []
        for h in headlines:
            score = 50 + len(h) // 5
            if "ultimate" in h.lower() or "guide" in h.lower():
                score += 15
            if any(x in h.lower() for x in ["5", "10", "best", "master"]):
                score += 10
            scores.append(min(100, score))
            
        winner_idx = scores.index(max(scores))
        return jsonify({
            "success": True,
            "results": [{"headline": h, "score": s} for h, s in zip(headlines, scores)],
            "winner": headlines[winner_idx],
            "winner_score": scores[winner_idx]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 200

if __name__ == "__main__":
    # Start on standard port 5050
    app.run(host="0.0.0.0", port=5050, debug=False)
