# ✅ DevPulse - Complete & Working Guide

## 🚀 How to Run

```bash
cd /Users/Dev/Ai-Agent-Hackathon
source venv/bin/activate
python ui/api_server.py
```

Then open: **http://localhost:5050**

---

## ✨ Features & How to Use

### 📊 Dashboard Tab
*   **Run Analysis**: Click **🔄 Run Analysis** to trigger the background analytical engine.
*   **Performance Metrics Grid**: Highlights total articles analyzed, active topics covered, insight count, and the best content format.
*   **Interactive Chart**: Re-renders a topic performance overview bar chart using Chart.js.
*   **Key Insights**: Lists dynamically generated observations matching your active dataset.

### ✍️ Draft Scorer Tab (Multimodal Support)
*   **Metadata & Markdown**: Enter your title, topic, format, audience, word count, and paste draft content.
*   **📸 Screenshot/Video Asset Upload**: Choose an optional screenshot (PNG/JPG) or video (MP4/MOV) asset.
*   **Performance Evaluation**: Click **📈 Score This Draft** to run visual dimension checks, apply a +0 to +10 score boost, and retrieve scoring suggestions.

### 🔀 A/B Tester Tab
*   **Headline Variant Testing**: Input up to 3 different headline variants.
*   **Compare**: Click **🔀 Run A/B Performance Test** to compare conversions performance. The top variant is highlighted with a gold border and a `🏆 Top Performer` trophy badge.

### 📤 Custom Data Tab
*   **Add Content Manually**: Form input to add content. Dropdowns are populated directly from `config.py` definitions (`config.TOPICS`, `config.FORMATS`, `config.AUDIENCE_SEGMENTS`) to ensure validation passes.
*   **Bulk CSV Ingest**: Click or drag-and-drop a content CSV file onto the upload zone, then click **🚀 Load and Parse File** to append bulk performance metrics.

### 🎯 Strategy Tab
*   **Strategy Report**: Click **📊 Generate Report** to run the complete collaborative agent pipeline.
*   **Recommendations**: Displays dynamic `What to Continue`, `What to Stop`, and `Gaps to Create Next` lists.
*   **Collaborative Trace Log**: Expandable trace log timeline displaying execution times and summaries for each agent (Collector -> Analyzer -> Strategist -> Report).

### 📋 Data Table Tab
*   **Content Database Explorer**: View the loaded content database rows (Title, Topic, Format, Views, Conversions, Score).

---

## 🎨 UI Features
*   ✅ **Dark Glow Aesthetics** - Premium dark layout with glowing cards.
*   ✅ **Micro-Animations** - Subtle scale changes (`transform: scale(0.97)`) on click active buttons.
*   ✅ **Visual Hierarchy** - Semantic headings in each section matching the content.
*   ✅ **Dynamic State Synchronization** - All widgets refresh instantly when you add custom inputs or upload files.
