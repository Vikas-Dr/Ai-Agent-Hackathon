// ContentPulse Dashboard App

class ContentPulseApp {
    constructor() {
        this.state = {
            report: null,
            analysis: null,
            scoreResult: null,
            trace: null,
        };
        this.topics = [];
        this.formats = [];
        this.audiences = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadConfig();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Dashboard
        document.getElementById('btn-run-analysis').addEventListener('click', () => this.runAnalysis());

        // Scorer
        document.getElementById('scorer-form').addEventListener('submit', (e) => this.scoreContent(e));

        // Strategy
        document.getElementById('btn-generate-report').addEventListener('click', () => this.generateReport());
    }

    async loadConfig() {
        try {
            const [topicsRes, formatsRes, audiencesRes] = await Promise.all([
                fetch('/api/topics'),
                fetch('/api/formats'),
                fetch('/api/audiences'),
            ]);

            this.topics = await topicsRes.json();
            this.formats = await formatsRes.json();
            this.audiences = await audiencesRes.json();

            this.populateSelects();
        } catch (e) {
            console.error('Error loading config:', e);
        }
    }

    populateSelects() {
        const topicSelect = document.getElementById('scorer-topic');
        const formatSelect = document.getElementById('scorer-format');
        const audienceSelect = document.getElementById('scorer-audience');

        this.topics.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            topicSelect.appendChild(opt);
        });

        this.formats.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f;
            opt.textContent = f;
            formatSelect.appendChild(opt);
        });

        this.audiences.forEach(a => {
            const opt = document.createElement('option');
            opt.value = a;
            opt.textContent = a;
            audienceSelect.appendChild(opt);
        });
    }

    switchTab(tabName) {
        // Remove active from all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active to selected
        document.getElementById(tabName).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }

    async runAnalysis() {
        try {
            document.getElementById('btn-run-analysis').disabled = true;
            document.getElementById('btn-run-analysis').textContent = '⏳ Running...';

            const response = await fetch('/api/report', { method: 'POST' });
            const data = await response.json();

            this.state.report = data.report;
            this.state.analysis = data.analysis;
            this.state.trace = data.trace;

            this.renderDashboard();
        } catch (e) {
            console.error('Error running analysis:', e);
            alert('Failed to run analysis: ' + e.message);
        } finally {
            document.getElementById('btn-run-analysis').disabled = false;
            document.getElementById('btn-run-analysis').textContent = '🔄 Run Analysis';
        }
    }

    renderDashboard() {
        const analysis = this.state.analysis;
        const report = this.state.report;

        // Update metrics
        document.getElementById('metric-articles').textContent = 
            Object.values(this.getTopicCounts()).reduce((a, b) => a + b, 0);
        document.getElementById('metric-topics').textContent = 
            analysis.top_topics.length;
        document.getElementById('metric-insights').textContent = 
            analysis.insights.length;
        document.getElementById('metric-gaps').textContent = 
            report.create_next.length;

        // Render charts
        this.renderBarChart(
            'chart-topics',
            analysis.top_topics.map(t => ({
                label: t.topic,
                value: t.avg_score,
                count: t.count,
            }))
        );

        this.renderBarChart(
            'chart-formats',
            analysis.top_formats.map(f => ({
                label: f.format,
                value: f.avg_score,
                count: f.count,
            }))
        );

        // Render insights
        const insightsList = document.getElementById('insights-list');
        insightsList.innerHTML = '';
        analysis.insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
        });

        // Render trace
        this.renderTrace('trace-dashboard', this.state.trace);
    }

    renderBarChart(containerId, data) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        const maxValue = Math.max(...data.map(d => d.value));

        data.forEach(item => {
            const row = document.createElement('div');
            row.className = 'bar-row';

            const percentage = (item.value / maxValue) * 100;

            row.innerHTML = `
                <div class="bar-label">${item.label}</div>
                <div class="bar-track">
                    <div class="bar-fill" style="width: ${percentage}%"></div>
                </div>
                <div class="bar-value">${item.value.toFixed(1)}</div>
            `;

            container.appendChild(row);
        });
    }

    renderTrace(containerId, trace) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        trace.entries.forEach(entry => {
            const div = document.createElement('div');
            div.className = 'trace-entry';
            div.innerHTML = `
                <div class="trace-agent">${entry.agent}</div>
                <div class="trace-status ${entry.status}">${entry.status}</div>
                <div class="trace-detail">${entry.output_summary}</div>
                <div class="trace-duration">${entry.duration_seconds.toFixed(3)}s</div>
            `;
            container.appendChild(div);
        });
    }

    async scoreContent(e) {
        e.preventDefault();

        try {
            const payload = {
                title: document.getElementById('scorer-title').value,
                topic: document.getElementById('scorer-topic').value,
                format: document.getElementById('scorer-format').value,
                audience_segment: document.getElementById('scorer-audience').value,
                word_count: parseInt(document.getElementById('scorer-wordcount').value),
                draft_markdown: document.getElementById('scorer-markdown').value || null,
            };

            const response = await fetch('/api/score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Scoring failed');
            }

            const data = await response.json();
            this.state.scoreResult = data.prediction;

            this.renderScoreResult(data.prediction);
        } catch (e) {
            console.error('Error scoring content:', e);
            alert('Scoring failed: ' + e.message);
        }
    }

    renderScoreResult(prediction) {
        const resultCard = document.getElementById('score-result');
        resultCard.classList.remove('hidden');

        const score = prediction.predicted_score;
        const circumference = 282.6;
        const offset = circumference - (score / 100) * circumference;

        const fillCircle = document.querySelector('.score-ring-fill');
        fillCircle.style.strokeDashoffset = offset;

        // Color based on score
        if (score >= 70) {
            fillCircle.style.stroke = '#48c482';
        } else if (score >= 40) {
            fillCircle.style.stroke = '#fbbf24';
        } else {
            fillCircle.style.stroke = '#ef5350';
        }

        document.getElementById('result-score').textContent = score;
        document.getElementById('result-reasoning').textContent = prediction.reasoning;

        // Render code ratio bar
        const codeRatio = prediction.code_to_text_ratio || 0;
        const codeRatioPercent = Math.round(codeRatio * 100);
        document.getElementById('result-code-ratio-fill').style.width = `${codeRatioPercent}%`;
        document.getElementById('result-code-ratio-percent').textContent = `${codeRatioPercent}%`;

        // Render code quality feedback
        const codeFeedback = prediction.code_quality_feedback || 'No code analysis available';
        document.getElementById('result-code-feedback').textContent = codeFeedback;

        const confidenceEl = document.getElementById('result-confidence');
        confidenceEl.className = `confidence-badge ${prediction.confidence}`;
        confidenceEl.textContent = prediction.confidence.toUpperCase();

        const suggestionsList = document.getElementById('result-suggestions');
        suggestionsList.innerHTML = '';
        prediction.suggestions.forEach(s => {
            const li = document.createElement('li');
            li.textContent = s;
            suggestionsList.appendChild(li);
        });

        document.getElementById('result-comparable').textContent = prediction.comparable_count;

        // Scroll to result
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    getTopicCounts() {
        const counts = {};
        this.state.analysis?.top_topics.forEach(t => {
            counts[t.topic] = t.count;
        });
        return counts;
    }

    async generateReport() {
        try {
            document.getElementById('btn-generate-report').disabled = true;
            document.getElementById('btn-generate-report').textContent = '⏳ Generating...';

            const response = await fetch('/api/report', { method: 'POST' });
            const data = await response.json();

            this.state.report = data.report;
            this.state.analysis = data.analysis;
            this.state.trace = data.trace;

            this.renderReport();
        } catch (e) {
            console.error('Error generating report:', e);
            alert('Report generation failed: ' + e.message);
        } finally {
            document.getElementById('btn-generate-report').disabled = false;
            document.getElementById('btn-generate-report').textContent = '📋 Generate Report';
        }
    }

    renderReport() {
        const report = this.state.report;
        const container = document.getElementById('report-container');
        container.innerHTML = '';

        // Header
        const header = document.createElement('div');
        header.className = 'report-header';
        header.innerHTML = `
            <h2>Editorial Strategy Report</h2>
            <p>Generated: ${new Date(report.report_date).toLocaleDateString()} | Period: ${report.period}</p>
            <p>${report.summary}</p>
        `;
        container.appendChild(header);

        // Cards grid
        const grid = document.createElement('div');
        grid.className = 'report-cards';

        // Continue items
        const continueCard = this.createReportCard(
            'continue',
            `Continue (${report.continue_items.length})`,
            report.continue_items
        );
        grid.appendChild(continueCard);

        // Stop items
        const stopCard = this.createReportCard(
            'stop',
            `Stop (${report.stop_items.length})`,
            report.stop_items
        );
        grid.appendChild(stopCard);

        // Create next
        const createCard = this.createReportCard(
            'create',
            `Create Next (${report.create_next.length})`,
            report.create_next
        );
        grid.appendChild(createCard);

        container.appendChild(grid);

        // Trace
        this.renderTrace('trace-strategy', this.state.trace);
    }

    createReportCard(cardClass, title, items) {
        const card = document.createElement('div');
        card.className = `report-card ${cardClass}`;

        const h3 = document.createElement('h3');
        h3.textContent = title;
        card.appendChild(h3);

        const itemsContainer = document.createElement('div');
        itemsContainer.className = 'report-items';

        items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'report-item';

            if (item.topic) {
                itemDiv.innerHTML = `
                    <strong>${item.topic}</strong> (${item.format})<br>
                    <div class="item-reason">${item.reason}</div>
                `;
            } else {
                itemDiv.textContent = item;
            }

            itemsContainer.appendChild(itemDiv);
        });

        card.appendChild(itemsContainer);
        return card;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ContentPulseApp();
});
