from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
from pathlib import Path
import io
import csv

# Initialize Flask
UI_PATH = Path(__file__).parent
app = Flask(__name__, static_folder=str(UI_PATH), template_folder=str(UI_PATH))
CORS(app)

# Mock data storage
stored_data = []
llm_suggestions_cache = {}

# ==================== ROUTES ====================

@app.route("/")
def index():
    """Serve main dashboard."""
    with open(UI_PATH / "index.html", "r") as f:
        return f.read()

@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files (CSS, JS)."""
    file_path = UI_PATH / filename
    if file_path.exists():
        with open(file_path, "r") as f:
            if filename.endswith('.css'):
                return f.read(), 200, {'Content-Type': 'text/css'}
            elif filename.endswith('.js'):
                return f.read(), 200, {'Content-Type': 'application/javascript'}
            else:
                return f.read(), 200
    return "File not found", 404

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "DevPulse is running"}), 200

# ==================== API ENDPOINTS ====================

@app.route("/api/topics", methods=["GET"])
def get_topics():
    """Get available topics."""
    topics = [
        "API Design",
        "Authentication",
        "Backend Development",
        "Frontend Development",
        "DevOps",
        "Security",
        "Performance",
        "Testing",
        "Documentation",
        "Infrastructure"
    ]
    return jsonify(topics), 200

@app.route("/api/formats", methods=["GET"])
def get_formats():
    """Get available content formats."""
    formats = [
        "Blog Post",
        "Tutorial",
        "Guide",
        "Video Script",
        "Podcast Transcript",
        "Whitepaper",
        "Case Study"
    ]
    return jsonify(formats), 200

@app.route("/api/audiences", methods=["GET"])
def get_audiences():
    """Get audience segments."""
    audiences = [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert"
    ]
    return jsonify(audiences), 200

@app.route("/api/data", methods=["GET"])
def get_data():
    """Get stored data with pagination."""
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    paginated = stored_data[offset:offset+limit]
    return jsonify({
        "rows": paginated,
        "total": len(stored_data),
        "limit": limit,
        "offset": offset
    }), 200

@app.route("/api/add-data", methods=["POST"])
def add_data():
    """Add new data entry."""
    try:
        data = request.get_json()
        entry = {
            "title": data.get("title"),
            "topic": data.get("topic"),
            "format": data.get("format"),
            "audience": data.get("audience"),
            "wordcount": data.get("wordcount", 0),
            "views": data.get("views", 0),
            "performance_score": data.get("score", 75)
        }
        stored_data.append(entry)
        return jsonify({
            "success": True,
            "message": f"✅ Added: {entry['title']}",
            "entry": entry
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/score", methods=["POST"])
def score_content():
    """Score content based on criteria."""
    try:
        data = request.get_json()
        title = data.get("title", "Untitled")
        topic = data.get("topic", "General")
        wordcount = data.get("word_count", 1000)
        
        # Mock scoring logic
        base_score = 50
        if wordcount >= 1000:
            base_score += 10
        if wordcount >= 2000:
            base_score += 15
        if len(topic) > 3:
            base_score += 10
        
        score = min(100, max(0, base_score + (hash(title) % 30 - 15)))
        
        return jsonify({
            "prediction": {
                "predicted_score": score,
                "reasoning": f"Content '{title}' scored {score}/100 based on topic depth, word count ({wordcount}), and structure.",
                "suggestions": [
                    "✓ Add more examples to improve clarity",
                    "✓ Include code snippets for technical topics",
                    "✓ Add a summary section at the end",
                    "✓ Use better formatting and headers"
                ]
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/llm-suggest", methods=["POST"])
def llm_suggest():
    """Generate LLM suggestions."""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        content_type = data.get("type", "outline")
        tone = data.get("tone", "professional")
        
        # Mock LLM responses based on type
        responses = {
            "headline": [
                "🎯 Master API Design: Essential Practices for Modern Developers",
                "⚡ The Complete Guide to Building Scalable APIs",
                "🚀 5 Critical API Design Patterns You Need to Know",
                "💡 API Design Best Practices: From Theory to Production"
            ],
            "outline": [
                "<strong>I. Introduction</strong><br>- Why API design matters<br>- Real-world impact<br><br><strong>II. Core Concepts</strong><br>- REST principles<br>- RESTful design<br><br><strong>III. Best Practices</strong><br>- Error handling<br>- Documentation<br><br><strong>IV. Conclusion</strong><br>- Key takeaways"
            ],
            "summary": [
                "This content provides a comprehensive overview of API design principles. It emphasizes the importance of creating intuitive, scalable APIs that developers love to work with. Key topics include RESTful architecture, error handling, and comprehensive documentation."
            ],
            "keywords": [
                "API Design, REST Architecture, Developer Experience, API Documentation, Microservices, Authentication, Rate Limiting, API Security, GraphQL, Webhooks"
            ],
            "improvement": [
                "✓ Add practical code examples in multiple languages",
                "✓ Include performance benchmarks and metrics",
                "✓ Add a troubleshooting section",
                "✓ Include developer testimonials or case studies",
                "✓ Add interactive API playground examples"
            ]
        }
        
        suggestions = responses.get(content_type, responses["outline"])
        selected = suggestions[0] if suggestions else "No suggestions available"
        
        return jsonify({
            "success": True,
            "content": selected,
            "type": content_type,
            "tone": tone
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/report", methods=["POST"])
def generate_report():
    """Generate strategy report."""
    try:
        return jsonify({
            "analysis": {
                "top_topics": ["API Design", "Authentication", "Backend", "Frontend", "DevOps"],
                "top_formats": ["Blog Post", "Tutorial", "Guide"],
                "insights": [
                    "📊 API Design content performs 23% better than average",
                    "📈 Video tutorials have 40% higher engagement",
                    "💡 Beginner-level content reaches 2x wider audience",
                    "🎯 Blog posts combined with videos get 60% more shares",
                    "🚀 Step-by-step guides have lowest bounce rate"
                ]
            },
            "report": {
                "summary": "Based on your content analysis, API and backend topics are performing exceptionally well. Continue focusing on technical depth while increasing tutorial and video content.",
                "create_next": [
                    {"topic": "GraphQL APIs", "priority": "high"},
                    {"topic": "WebSocket Real-time APIs", "priority": "high"},
                    {"topic": "API Security Best Practices", "priority": "medium"},
                    {"topic": "Rate Limiting Strategies", "priority": "medium"},
                    {"topic": "API Documentation Tools", "priority": "low"}
                ]
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    """Handle CSV file upload."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        # Parse CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_data = csv.DictReader(stream)
        
        rows_processed = 0
        for row in csv_data:
            entry = {
                "title": row.get("title", "Untitled"),
                "topic": row.get("topic", "General"),
                "format": row.get("format", "Blog"),
                "views": int(row.get("views", 0)),
                "performance_score": int(row.get("score", 75))
            }
            stored_data.append(entry)
            rows_processed += 1
        
        return jsonify({
            "success": True,
            "rows_processed": rows_processed,
            "message": f"✅ Uploaded {rows_processed} rows"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/ab-test", methods=["POST"])
def ab_test():
    """Run A/B test on headlines."""
    try:
        data = request.get_json()
        headlines = data.get("headlines", [])
        
        if not headlines:
            return jsonify({"error": "No headlines provided"}), 400
        
        # Mock scoring based on word count and keywords
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
            "results": [
                {"headline": h, "score": s} for h, s in zip(headlines, scores)
            ],
            "winner": headlines[winner_idx],
            "winner_score": scores[winner_idx]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
