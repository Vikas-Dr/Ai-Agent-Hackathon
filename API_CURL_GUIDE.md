"""
DevPulse File Upload API - curl Command Guide
Complete reference for uploading CSV data and multimodal assets via HTTP
"""

# ==================== QUICK START ====================

# Upload Custom CSV Dataset:
# curl -X POST http://localhost:5050/api/upload-csv -F "file=@data/sample_content_data.csv"

# Upload Screenshot/Video:
# curl -X POST http://localhost:5050/api/upload-asset -F "file=@architecture.png"

# Score Draft with Asset:
# curl -X POST http://localhost:5050/api/score \
#   -H "Content-Type: application/json" \
#   -d '{"title":"...", "topic":"API Design", "format":"tutorial", "audience_segment":"backend", "word_count":2000, "asset_path":"/assets/user_uploads/architecture.png"}'

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    DevPulse File Upload API - curl Guide                      ║
╚═══════════════════════════════════════════════════════════════════════════════╝

1️⃣  UPLOAD CUSTOM CSV DATASET
─────────────────────────────────────────────────────────────────────────────────

POST /api/upload-csv

Basic Upload:
  curl -X POST http://localhost:5050/api/upload-csv \\
    -F "file=@data/sample_content_data.csv"

With Verbose Output:
  curl -v -X POST http://localhost:5050/api/upload-csv \\
    -F "file=@data/sample_content_data.csv"

Success Response (JSON):
  {
    "message": "Custom dataset processed successfully",
    "filename": "sample_content_data.csv",
    "rows_processed": 95,
    "result": {
      "report": {
        "summary": "DevRel Report: Continue investing in..."
      }
    }
  }

─────────────────────────────────────────────────────────────────────────────────

2️⃣  UPLOAD ASSET (SCREENSHOT/VIDEO)
─────────────────────────────────────────────────────────────────────────────────

POST /api/upload-asset

Upload PNG Screenshot:
  curl -X POST http://localhost:5050/api/upload-asset \\
    -F "file=@screenshots/architecture.png"

Upload Video:
  curl -X POST http://localhost:5050/api/upload-asset \\
    -F "file=@videos/demo.mp4"

Supported Formats:
  ✓ Images: PNG, JPG, JPEG, GIF, WebP
  ✓ Videos: MP4, MOV, AVI, WebM
  ✓ Max Size: 50MB

Success Response (JSON):
  {
    "message": "Asset uploaded successfully",
    "asset_path": "/assets/user_uploads/architecture.png",
    "asset_name": "architecture.png",
    "asset_type": "image",
    "file_size": 2048576
  }

─────────────────────────────────────────────────────────────────────────────────

3️⃣  SCORE DRAFT WITH OPTIONAL ASSET
─────────────────────────────────────────────────────────────────────────────────

POST /api/score (Enhanced)

Score with Multimodal Asset:
  curl -X POST http://localhost:5050/api/score \\
    -H "Content-Type: application/json" \\
    -d '{
      "title": "Building REST APIs with FastAPI",
      "topic": "API Design",
      "format": "tutorial",
      "audience_segment": "backend",
      "word_count": 2000,
      "draft_markdown": "# FastAPI\\n\\n```python\\nfrom fastapi import FastAPI\\napp = FastAPI()\\n```",
      "asset_path": "/assets/user_uploads/architecture.png"
    }'

Score Without Asset:
  curl -X POST http://localhost:5050/api/score \\
    -H "Content-Type: application/json" \\
    -d '{
      "title": "API Design Best Practices",
      "topic": "API Design",
      "format": "blog",
      "audience_segment": "backend",
      "word_count": 1500
    }'

Success Response (JSON):
  {
    "prediction": {
      "predicted_score": 82,
      "reasoning": "Strong tutorial format targeting backend developers",
      "suggestions": [
        "Add runnable code in first 200 words",
        "Include curl command for quick start",
        "Optimize for API keywords"
      ],
      "confidence": "high",
      "comparable_count": 12,
      "code_quality_feedback": "Good code ratio. Add error handling.",
      "code_to_text_ratio": 0.25
    }
  }

─────────────────────────────────────────────────────────────────────────────────

4️⃣  COMPLETE WORKFLOW EXAMPLE
─────────────────────────────────────────────────────────────────────────────────

Step 1: Upload CSV
  curl -X POST http://localhost:5050/api/upload-csv \\
    -F "file=@my_content_data.csv"

Step 2: Upload Asset
  curl -X POST http://localhost:5050/api/upload-asset \\
    -F "file=@diagram.png"

Step 3: Get asset_path from response
  ASSET_PATH="/assets/user_uploads/diagram.png"

Step 4: Score Draft with Asset
  curl -X POST http://localhost:5050/api/score \\
    -H "Content-Type: application/json" \\
    -d '{
      "title": "My Article",
      "topic": "API Design",
      "format": "tutorial",
      "audience_segment": "backend",
      "word_count": 2000,
      "asset_path": "'$ASSET_PATH'"
    }'

─────────────────────────────────────────────────────────────────────────────────

5️⃣  CURL OPTIONS & FLAGS
─────────────────────────────────────────────────────────────────────────────────

File Upload:
  -F "file=@path"      Upload file (multipart form)
  -F "file=@-"         Upload from stdin

Headers & Content:
  -H "Header: Value"   Custom header
  -H "Content-Type"    Specify content type
  -d '{JSON}'          Send JSON data

Output & Display:
  -v                   Verbose output (show headers)
  -i                   Include response headers
  -s                   Silent (no progress)
  -w "%{http_code}"    Show HTTP status code
  -o filename          Save to file
  > output.json        Redirect to file

Timeouts & Limits:
  --max-time 30        30 second timeout
  --compressed         Enable compression

─────────────────────────────────────────────────────────────────────────────────

6️⃣  PRETTY-PRINT JSON RESPONSES
─────────────────────────────────────────────────────────────────────────────────

Using jq (recommended):
  curl ... | jq '.'
  curl ... | jq '.prediction.predicted_score'

Using Python:
  curl ... | python -m json.tool
  curl ... | python -c "import sys, json; print(json.load(sys.stdin)['prediction'])"

Using grep:
  curl ... | grep -o '"predicted_score":[0-9]*'

─────────────────────────────────────────────────────────────────────────────────

7️⃣  REAL-WORLD EXAMPLES
─────────────────────────────────────────────────────────────────────────────────

Upload your company's content data:
  curl -X POST http://localhost:5050/api/upload-csv \\
    -F "file=@company_content.csv"

Upload architecture diagram:
  curl -X POST http://localhost:5050/api/upload-asset \\
    -F "file=@system_architecture.png"

Score a technical blog post with diagram:
  curl -X POST http://localhost:5050/api/score \\
    -H "Content-Type: application/json" \\
    -d '{
      "title": "Microservices Architecture Guide",
      "topic": "Cloud Infrastructure",
      "format": "technical_blog",
      "audience_segment": "architects",
      "word_count": 3000,
      "draft_markdown": "...",
      "asset_path": "/assets/user_uploads/microservices_diagram.png"
    }'

Export results:
  curl -X POST http://localhost:5050/api/upload-csv \\
    -F "file=@data.csv" | jq '.' > analysis.json

─────────────────────────────────────────────────────────────────────────────────

8️⃣  TROUBLESHOOTING
─────────────────────────────────────────────────────────────────────────────────

Connection refused:
  • Verify server running: PYTHONPATH=. python ui/api_server.py
  • Check port: http://localhost:5050 (not https)
  • Firewall may be blocking port 5050

File not found:
  • Use absolute path: curl -F "file=@$(pwd)/data/file.csv"
  • Or change to file directory: cd /path/to/file && curl -F "file=@file.csv"

Invalid file format:
  • CSV endpoint only accepts .csv
  • Asset endpoint: png, jpg, jpeg, gif, webp, mp4, mov, avi, webm
  • Check file extension

Missing required fields:
  • Ensure all required fields in JSON: title, topic, format, audience_segment, word_count
  • audience_segment: must be one of: frontend, backend, devops, architects
  • topic: must be from configured topics list

413 Payload Too Large:
  • File exceeds 50MB limit
  • Compress or split files

─────────────────────────────────────────────────────────────────────────────────

9️⃣  PERFORMANCE & LIMITS
─────────────────────────────────────────────────────────────────────────────────

File Limits:
  • Max file size: 50MB
  • Max CSV rows: 100,000+
  • Max concurrent uploads: 5-10 (depending on server)

Timeout Recommendations:
  • Small files (<5MB): 10 seconds
  • Medium files (5-20MB): 30 seconds
  • Large files (20-50MB): 60 seconds

Rate Limiting:
  • No rate limiting by default
  • Recommended: 1-2 uploads per second
  • Batch processing: Groups of 5-10 files

─────────────────────────────────────────────────────────────────────────────────

🔟 QUICK REFERENCE
─────────────────────────────────────────────────────────────────────────────────

Start Server:
  PYTHONPATH=. python ui/api_server.py

Upload CSV:
  curl -X POST http://localhost:5050/api/upload-csv -F "file=@data/sample_content_data.csv"

Upload Asset:
  curl -X POST http://localhost:5050/api/upload-asset -F "file=@screenshot.png"

Score Draft:
  curl -X POST http://localhost:5050/api/score -H "Content-Type: application/json" \\
    -d '{"title":"My Article","topic":"API Design","format":"tutorial","audience_segment":"backend","word_count":2000}'

Pretty-print:
  curl ... | python -m json.tool

Check Status:
  curl http://localhost:5050/api/topics

═══════════════════════════════════════════════════════════════════════════════════
""")
