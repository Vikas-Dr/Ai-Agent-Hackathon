#!/bin/bash

# DevPulse File Upload API Workflow Script
# Automates CSV upload → Asset upload → Draft scoring
# Usage: bash upload_workflow.sh [csv_file] [image_file]

set -e

# ==================== CONFIGURATION ====================

API_URL="http://localhost:5050"
CSV_FILE="${1:-data/sample_content_data.csv}"
IMAGE_FILE="${2:-}"
OUTPUT_DIR="api_results"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# ==================== MAIN WORKFLOW ====================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       DevPulse File Upload API Workflow                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🔧 Configuration:"
echo "   API URL: $API_URL"
echo "   CSV File: $CSV_FILE"
echo "   Image File: ${IMAGE_FILE:-None}"
echo ""

# ==================== STEP 1: Upload CSV ====================

echo "📁 STEP 1: Uploading CSV Dataset..."
echo "   File: $CSV_FILE"

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ Error: CSV file not found: $CSV_FILE"
    exit 1
fi

CSV_RESPONSE=$(curl -s -X POST "$API_URL/api/upload-csv" -F "file=@$CSV_FILE")

if echo "$CSV_RESPONSE" | grep -q "error"; then
    echo "❌ CSV Upload Failed:"
    echo "$CSV_RESPONSE"
    exit 1
fi

echo "✅ CSV Upload Success!"
echo "$CSV_RESPONSE" | python -m json.tool > "$OUTPUT_DIR/01_csv_upload.json" 2>/dev/null || echo "$CSV_RESPONSE" > "$OUTPUT_DIR/01_csv_upload.json"

# Extract rows processed
CSV_ROWS=$(echo "$CSV_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['rows_processed'])" 2>/dev/null || echo "0")
echo "   Rows processed: $CSV_ROWS"
echo ""

# ==================== STEP 2: Upload Asset (Optional) ====================

ASSET_PATH=""
if [ -n "$IMAGE_FILE" ] && [ -f "$IMAGE_FILE" ]; then
    echo "📸 STEP 2: Uploading Asset..."
    echo "   File: $IMAGE_FILE"
    
    ASSET_RESPONSE=$(curl -s -X POST "$API_URL/api/upload-asset" -F "file=@$IMAGE_FILE")
    
    if echo "$ASSET_RESPONSE" | grep -q "error"; then
        echo "⚠️  Asset Upload Failed (continuing without asset):"
        echo "$ASSET_RESPONSE"
    else
        echo "✅ Asset Upload Success!"
        echo "$ASSET_RESPONSE" | python -m json.tool > "$OUTPUT_DIR/02_asset_upload.json" 2>/dev/null || echo "$ASSET_RESPONSE" > "$OUTPUT_DIR/02_asset_upload.json"
        
        ASSET_PATH=$(echo "$ASSET_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['asset_path'])" 2>/dev/null)
        echo "   Asset path: $ASSET_PATH"
    fi
else
    echo "⏭️  STEP 2: Skipped (no image file provided)"
fi
echo ""

# ==================== STEP 3: Score Draft ====================

echo "📊 STEP 3: Scoring Draft Content..."

# Build payload
PAYLOAD='{
  "title": "Building REST APIs with FastAPI",
  "topic": "API Design",
  "format": "tutorial",
  "audience_segment": "backend",
  "word_count": 2000,
  "draft_markdown": "# FastAPI Tutorial\n\n```python\nfrom fastapi import FastAPI\napp = FastAPI()\n\n@app.get(\"/items/{item_id}\")\nasync def read_item(item_id: int):\n    return {\"item_id\": item_id}\n```\n\nThis guide covers building production-ready REST APIs with FastAPI, including authentication, error handling, and deployment strategies."'

# Add asset path if available
if [ -n "$ASSET_PATH" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | python -c "import sys,json; d=json.load(sys.stdin); d['asset_path']='$ASSET_PATH'; print(json.dumps(d))" 2>/dev/null || echo "$PAYLOAD")
fi

SCORE_RESPONSE=$(curl -s -X POST "$API_URL/api/score" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

if echo "$SCORE_RESPONSE" | grep -q "error"; then
    echo "❌ Draft Scoring Failed:"
    echo "$SCORE_RESPONSE"
    exit 1
fi

echo "✅ Draft Scoring Success!"
echo "$SCORE_RESPONSE" | python -m json.tool > "$OUTPUT_DIR/03_score_response.json" 2>/dev/null || echo "$SCORE_RESPONSE" > "$OUTPUT_DIR/03_score_response.json"

# Extract score and confidence
SCORE=$(echo "$SCORE_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['prediction']['predicted_score'])" 2>/dev/null || echo "N/A")
CONFIDENCE=$(echo "$SCORE_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['prediction']['confidence'])" 2>/dev/null || echo "N/A")
CODE_RATIO=$(echo "$SCORE_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['prediction']['code_to_text_ratio'])" 2>/dev/null || echo "N/A")

echo "   Score: $SCORE/100"
echo "   Confidence: $CONFIDENCE"
echo "   Code Ratio: $CODE_RATIO"
echo ""

# ==================== SUMMARY ====================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 ✅ Workflow Complete                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "   CSV Rows: $CSV_ROWS"
echo "   Asset: $([ -z "$ASSET_PATH" ] && echo "Not uploaded" || echo "✓ $ASSET_PATH")"
echo "   Draft Score: $SCORE/100"
echo "   Confidence: $CONFIDENCE"
echo "   Code-to-Text Ratio: $CODE_RATIO"
echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
echo "   • 01_csv_upload.json"
[ -n "$ASSET_PATH" ] && echo "   • 02_asset_upload.json"
echo "   • 03_score_response.json"
echo ""
echo "✨ Done! Check results directory for detailed output."
echo ""
