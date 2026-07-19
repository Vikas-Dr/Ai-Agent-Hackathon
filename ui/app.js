// ContentPulse Dashboard App

class ContentPulseApp {
    constructor() {
        this.state = {
            report: null,
            analysis: null,
            scoreResult: null,
            trace: null,
            charts: {} // Store Chart.js instances for cleanup
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
        document.getElementById('btn-export-github').addEventListener('click', () => this.exportToGitHubIssues());
        const exportPdfBtn = document.getElementById('btn-export-pdf');
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', () => this.exportToPDF());
        }

        // A/B Tester
        document.getElementById('btn-run-ab-test').addEventListener('click', () => this.runABTest());

        // Custom Dataset
        document.getElementById('btn-analyze-custom').addEventListener('click', () => this.uploadCSVFile());
        this.setupFileDragDrop();
    }

    setupFileDragDrop() {
        // CSV drag-drop
        const csvZone = document.getElementById('csv-upload-zone');
        if (csvZone) {
            csvZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                csvZone.classList.add('drag-over');
            });
            csvZone.addEventListener('dragleave', () => csvZone.classList.remove('drag-over'));
            csvZone.addEventListener('drop', (e) => {
                e.preventDefault();
                csvZone.classList.remove('drag-over');
                const file = e.dataTransfer.files[0];
                if (file && file.name.endsWith('.csv')) {
                    document.getElementById('custom-csv-file').files = e.dataTransfer.files;
                    document.getElementById('csv-name').textContent = file.name;
                    document.getElementById('csv-preview').classList.remove('hidden');
                }
            });
            csvZone.addEventListener('click', () => document.getElementById('custom-csv-file').click());
        }

        // Asset drag-drop
        const assetZone = document.getElementById('file-upload-zone');
        if (assetZone) {
            assetZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                assetZone.classList.add('drag-over');
            });
            assetZone.addEventListener('dragleave', () => assetZone.classList.remove('drag-over'));
            assetZone.addEventListener('drop', (e) => {
                e.preventDefault();
                assetZone.classList.remove('drag-over');
                const file = e.dataTransfer.files[0];
                if (file) {
                    document.getElementById('scorer-asset').files = e.dataTransfer.files;
                    document.getElementById('asset-name').textContent = file.name;
                    document.getElementById('asset-preview').classList.remove('hidden');
                }
            });
            assetZone.addEventListener('click', () => document.getElementById('scorer-asset').click());
        }
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

    // ==================== CHART.JS UTILITIES ====================

    destroyChart(chartId) {
        if (this.state.charts[chartId]) {
            this.state.charts[chartId].destroy();
            delete this.state.charts[chartId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.state.charts).forEach(key => {
            this.state.charts[key].destroy();
        });
        this.state.charts = {};
    }

    createBarChart(canvasId, labels, values, label, color = '#48c482') {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.state.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    backgroundColor: color,
                    borderColor: color,
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleColor: '#48c482',
                        bodyColor: '#e2e8f0'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(71, 85, 105, 0.2)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    createDoughnutChart(canvasId, labels, values, colors = null) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const defaultColors = ['#48c482', '#2dd4bf', '#38bdf8', '#a78bfa', '#fbbf24', '#f472b6'];
        const chartColors = colors || defaultColors.slice(0, labels.length);

        this.state.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: chartColors,
                    borderColor: '#161a24',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#e2e8f0', padding: 15 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        bodyColor: '#e2e8f0'
                    }
                }
            }
        });
    }

    createLineChart(canvasId, labels, datasets) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const colors = ['#48c482', '#38bdf8', '#a78bfa', '#fbbf24'];
        const formattedDatasets = datasets.map((ds, idx) => ({
            label: ds.label,
            data: ds.data,
            borderColor: colors[idx % colors.length],
            backgroundColor: colors[idx % colors.length] + '15',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 4,
            pointBackgroundColor: colors[idx % colors.length]
        }));

        this.state.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: formattedDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        bodyColor: '#e2e8f0'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(71, 85, 105, 0.2)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: 'rgba(71, 85, 105, 0.2)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    createScatterChart(canvasId, data) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.state.charts[canvasId] = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Historical Content',
                    data: data.historical || [],
                    backgroundColor: 'rgba(72, 196, 130, 0.4)',
                    borderColor: '#48c482',
                    borderWidth: 1,
                    pointRadius: 5
                }, {
                    label: 'Your Draft',
                    data: data.draft || [],
                    backgroundColor: '#fbbf24',
                    borderColor: '#f59e0b',
                    borderWidth: 2,
                    pointRadius: 8,
                    pointStyle: 'star'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0', padding: 15 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        bodyColor: '#e2e8f0',
                        callbacks: {
                            label: (ctx) => `Score: ${ctx.parsed.y.toFixed(1)}`
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Word Count', color: '#e2e8f0' },
                        grid: { color: 'rgba(71, 85, 105, 0.2)' },
                        ticks: { color: '#94a3b8' }
                    },
                    y: {
                        title: { display: true, text: 'Score', color: '#e2e8f0' },
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(71, 85, 105, 0.2)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    createRadarChart(canvasId, labels, values, label = 'Value') {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.state.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: values,
                    backgroundColor: 'rgba(72, 196, 130, 0.2)',
                    borderColor: '#48c482',
                    borderWidth: 2,
                    pointBackgroundColor: '#48c482',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0' }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        bodyColor: '#e2e8f0'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: { color: 'rgba(71, 85, 105, 0.2)' },
                        ticks: { color: '#94a3b8', backdropColor: 'transparent' }
                    }
                }
            }
        });
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

        // Destroy previous charts
        this.destroyAllCharts();

        // Update metric cards
        const totalArticles = Object.values(this.getTopicCounts()).reduce((a, b) => a + b, 0);
        document.getElementById('metric-articles').textContent = totalArticles;
        document.getElementById('metric-topics').textContent = analysis.top_topics.length;
        document.getElementById('metric-insights').textContent = analysis.insights.length;
        document.getElementById('metric-gaps').textContent = report.create_next.length;

        // ROW 1: Sparklines (mini charts)
        this.createSparklines();

        // ROW 1B: Best Topic & Format
        if (analysis.top_topics.length > 0) {
            document.getElementById('best-topic-name').textContent = analysis.top_topics[0].topic;
            document.getElementById('best-topic-score').textContent = `Score: ${analysis.top_topics[0].avg_score.toFixed(1)}`;
        }
        if (analysis.top_formats.length > 0) {
            document.getElementById('best-format-name').textContent = analysis.top_formats[0].format;
            document.getElementById('best-format-score').textContent = `Score: ${analysis.top_formats[0].avg_score.toFixed(1)}`;
        }

        // ROW 2: Charts
        // Topic Performance Bar Chart
        if (analysis.top_topics.length > 0) {
            const topicLabels = analysis.top_topics.map(t => t.topic);
            const topicValues = analysis.top_topics.map(t => t.avg_score);
            this.createBarChart('chart-topics-bar', topicLabels, topicValues, 'Avg Score', '#48c482');
        }

        // Format Distribution Doughnut
        if (analysis.top_formats.length > 0) {
            const formatLabels = analysis.top_formats.map(f => f.format);
            const formatCounts = analysis.top_formats.map(f => f.count);
            this.createDoughnutChart('chart-formats-doughnut', formatLabels, formatCounts);
        }

        // Audience Reach (if available)
        if (analysis.audiences && analysis.audiences.length > 0) {
            const audienceLabels = analysis.audiences.map(a => a.audience || a.name);
            const audienceValues = analysis.audiences.map(a => a.count || a.value);
            this.createBarChart('chart-audience-bar', audienceLabels, audienceValues, 'Reach', '#38bdf8');
        }

        // ROW 3: Trends & Length Distribution
        // Quarterly trends line chart (simulate with sample data if not available)
        if (analysis.quarterly_data) {
            const quarterLabels = Object.keys(analysis.quarterly_data);
            const datasets = [{
                label: 'Avg Score',
                data: Object.values(analysis.quarterly_data).map(q => q.avg_score)
            }];
            this.createLineChart('chart-trends-line', quarterLabels, datasets);
        }

        // Length buckets radar/bar chart
        if (analysis.length_distribution) {
            const lengthLabels = Object.keys(analysis.length_distribution);
            const lengthValues = Object.values(analysis.length_distribution);
            this.createRadarChart('chart-length-radar', lengthLabels, lengthValues, 'Content Count');
        }

        // ROW 4: Insights
        const insightsList = document.getElementById('insights-list');
        insightsList.innerHTML = '';
        analysis.insights.forEach(insight => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
        });

        // Data Table
        this.populateDataTable(analysis, report);

        // Render trace
        this.renderTrace('trace-dashboard', this.state.trace);
    }

    createSparklines() {
        const analysis = this.state.analysis;
        const sparklineIds = ['sparkline-articles', 'sparkline-topics', 'sparkline-insights', 'sparkline-gaps'];
        
        sparklineIds.forEach((id, idx) => {
            this.destroyChart(id);
            const ctx = document.getElementById(id);
            if (!ctx) return;

            // Generate mock trend data
            const data = {
                labels: ['W1', 'W2', 'W3', 'W4'],
                data: [Math.random() * 100, Math.random() * 100, Math.random() * 100, Math.random() * 100]
            };

            this.state.charts[id] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        borderColor: '#48c482',
                        backgroundColor: 'rgba(72, 196, 130, 0.1)',
                        borderWidth: 1,
                        fill: true,
                        pointRadius: 0,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            });
        });
    }

    populateDataTable(analysis, report) {
        const tbody = document.getElementById('data-table-body');
        tbody.innerHTML = '';

        const rows = [
            ['Total Articles', Object.values(this.getTopicCounts()).reduce((a, b) => a + b, 0)],
            ['Topics', analysis.top_topics.length],
            ['Formats', analysis.top_formats.length],
            ['Avg Score', analysis.top_topics.length > 0 ? (analysis.top_topics.reduce((sum, t) => sum + t.avg_score, 0) / analysis.top_topics.length).toFixed(1) : '—'],
            ['Content Gaps', report.create_next.length],
            ['Continue', report.continue_items.length],
            ['Stop', report.stop_items.length]
        ];

        rows.forEach(([label, value]) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${label}</td><td>${value}</td>`;
            tbody.appendChild(tr);
        });
    }

    async scoreContent(e) {
        e.preventDefault();

        try {
            document.querySelector('.scorer-form .btn-primary').disabled = true;
            document.querySelector('.scorer-form .btn-primary').textContent = '⏳ Scoring...';

            const payload = {
                title: document.getElementById('scorer-title').value,
                topic: document.getElementById('scorer-topic').value,
                format: document.getElementById('scorer-format').value,
                audience: document.getElementById('scorer-audience').value,
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
        } finally {
            document.querySelector('.scorer-form .btn-primary').disabled = false;
            document.querySelector('.scorer-form .btn-primary').textContent = '📈 Score This Draft';
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

        // Populate comparable content table
        this.populateComparableTable(prediction.comparable_items || []);

        // Render scatter chart
        const scatterData = {
            historical: (prediction.comparable_items || []).map(item => ({
                x: item.word_count || 1500,
                y: item.score || 75
            })),
            draft: [{ x: document.getElementById('scorer-wordcount').value, y: score }]
        };
        this.createScatterChart('chart-draft-vs-historical', scatterData);

        // Scroll to result
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    populateComparableTable(items) {
        const tbody = document.getElementById('comparable-table-body');
        tbody.innerHTML = '';

        if (!items || items.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="4" style="text-align: center; color: #94a3b8;">No comparable content found</td>';
            tbody.appendChild(tr);
            return;
        }

        items.slice(0, 5).forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${(item.title || 'Untitled').substring(0, 30)}...</td>
                <td>${item.topic || '—'}</td>
                <td>${item.format || '—'}</td>
                <td><strong>${item.score || '—'}</strong></td>
            `;
            tbody.appendChild(tr);
        });
    }

    uploadCSVFile() {
        const fileInput = document.getElementById('custom-csv-file');
        if (!fileInput || !fileInput.files.length) {
            alert('Please select a CSV file');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        document.getElementById('btn-analyze-custom').disabled = true;
        document.getElementById('btn-analyze-custom').textContent = '⏳ Analyzing...';

        fetch('/api/upload-csv', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(data => {
                document.getElementById('btn-analyze-custom').disabled = false;
                document.getElementById('btn-analyze-custom').textContent = '🚀 Run Custom Analysis';
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }

                const resultsDiv = document.getElementById('custom-results');
                const summaryDiv = document.getElementById('custom-report-summary');
                
                resultsDiv.classList.remove('hidden');
                summaryDiv.innerHTML = `
                    <div class="metric-card">
                        <div class="metric-label">Rows Processed</div>
                        <div class="metric-value">${data.rows_processed}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Status</div>
                        <div class="metric-value">✅ Complete</div>
                    </div>
                `;

                if (data.result?.report?.summary) {
                    summaryDiv.innerHTML += `<p>${data.result.report.summary}</p>`;
                }
            })
            .catch(e => {
                alert('Upload failed: ' + e.message);
                document.getElementById('btn-analyze-custom').disabled = false;
                document.getElementById('btn-analyze-custom').textContent = '🚀 Run Custom Analysis';
            });
    }

    uploadDraftAsset() {
        const fileInput = document.getElementById('scorer-asset');
        if (!fileInput || !fileInput.files.length) {
            return null;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        return fetch('/api/upload-asset', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    alert('Asset upload error: ' + data.error);
                    return null;
                }
                return data;
            })
            .catch(e => {
                console.error('Asset upload failed:', e);
                return null;
            });
    }

    runABTest() {
        try {
            // Collect headlines
            const headlines = [
                document.getElementById('headline-1')?.value || '',
                document.getElementById('headline-2')?.value || '',
                document.getElementById('headline-3')?.value || ''
            ].filter(h => h.trim());

            // Collect code hooks
            const hooks = [
                document.getElementById('hook-1')?.value || '',
                document.getElementById('hook-2')?.value || ''
            ].filter(h => h.trim());

            if (headlines.length === 0 || hooks.length === 0) {
                alert('Please enter at least 1 headline and 1 code hook');
                return;
            }

            // Simple client-side scoring
            const headlineResults = this.scoreHeadlines(headlines);
            const hookResults = this.scoreCodeHooks(hooks);

            this.renderABTestResults(headlineResults, hookResults);
        } catch (e) {
            console.error('A/B test failed:', e);
            alert('A/B test error: ' + e.message);
        }
    }

    scoreHeadlines(headlines) {
        const baselineScore = 75.0;
        const results = headlines.map((headline, i) => {
            const hasActionVerb = /build|create|learn|master|implement|optimize/i.test(headline);
            const hasKeyword = /api|tutorial|guide|python|rest|sdk/i.test(headline);
            
            let score = baselineScore;
            if (hasActionVerb) score += 15;
            if (hasKeyword) score += 10;
            if (headline.length > 70) score -= 5;
            score = Math.max(0, Math.min(100, score));

            return {
                headline,
                index: i + 1,
                score: Math.round(score * 10) / 10,
                has_action_verb: hasActionVerb,
                has_keyword: hasKeyword,
                variance_from_baseline: Math.round((score - baselineScore) * 10) / 10
            };
        });

        results.sort((a, b) => b.score - a.score);

        return {
            headlines: results,
            winner: results[0]?.headline || '',
            best_score: results[0]?.score || 0,
            average_score: Math.round((results.reduce((sum, r) => sum + r.score, 0) / results.length) * 10) / 10
        };
    }

    scoreCodeHooks(hooks) {
        const results = hooks.map((hook, i) => {
            const lines = hook.trim().split('\n');
            const codeLines = lines.filter(l => l.trim() && !l.trim().startsWith('#')).length;
            
            const isRunnable = /print\(|console\.log\(|puts /i.test(hook);
            const hasComments = /^[#/]/.test(hook.trim());
            const isPractical = /example|import|from|require|def |function/i.test(hook);

            let engagementScore = 60;
            if (isRunnable) engagementScore += 20;
            else engagementScore += 10;
            if (hasComments) engagementScore += 5;
            if (isPractical) engagementScore += 10;
            engagementScore = Math.max(0, Math.min(100, engagementScore));

            return {
                hook: hook.substring(0, 100) + (hook.length > 100 ? '...' : ''),
                full_hook: hook,
                index: i + 1,
                engagement_score: Math.round(engagementScore * 10) / 10,
                code_lines: codeLines,
                is_runnable: isRunnable,
                has_comments: hasComments,
                is_practical: isPractical
            };
        });

        results.sort((a, b) => b.engagement_score - a.engagement_score);

        return {
            hooks: results,
            winner: results[0]?.hook || '',
            best_engagement: results[0]?.engagement_score || 0,
            average_engagement: Math.round((results.reduce((sum, r) => sum + r.engagement_score, 0) / results.length) * 10) / 10
        };
    }

    renderABTestResults(headlineResults, hookResults) {
        const resultsDiv = document.getElementById('ab-results');
        resultsDiv.classList.remove('hidden');

        // Winner displays
        document.getElementById('ab-headline-winner').textContent = headlineResults.winner;
        document.getElementById('ab-headline-score').textContent = `Score: ${headlineResults.best_score}`;

        document.getElementById('ab-hook-winner').textContent = hookResults.winner;
        document.getElementById('ab-hook-score').textContent = `Engagement: ${hookResults.best_engagement}`;

        // Headlines table
        const headlineTable = document.getElementById('ab-headlines-table');
        headlineTable.innerHTML = '';
        headlineResults.headlines.forEach((h, idx) => {
            const isWinner = idx === 0;
            const row = document.createElement('tr');
            row.className = isWinner ? 'ab-winner' : '';
            row.innerHTML = `
                <td>${h.headline.substring(0, 60)}...</td>
                <td><strong>${h.score}</strong></td>
                <td>${h.has_action_verb ? '✓' : '✗'}</td>
                <td>${h.has_keyword ? '✓' : '✗'}</td>
                <td>${h.variance_from_baseline > 0 ? '+' : ''}${h.variance_from_baseline}</td>
            `;
            headlineTable.appendChild(row);
        });

        // Hooks table
        const hooksTable = document.getElementById('ab-hooks-table');
        hooksTable.innerHTML = '';
        hookResults.hooks.forEach((h, idx) => {
            const isWinner = idx === 0;
            const row = document.createElement('tr');
            row.className = isWinner ? 'ab-winner' : '';
            row.innerHTML = `
                <td>${h.hook.substring(0, 60)}...</td>
                <td><strong>${h.engagement_score}</strong></td>
                <td>${h.is_runnable ? '✓' : '✗'}</td>
                <td>${h.has_comments ? '✓' : '✗'}</td>
                <td>${h.is_practical ? '✓' : '✗'}</td>
            `;
            hooksTable.appendChild(row);
        });

        // Combined recommendation
        const recDiv = document.getElementById('ab-combined-rec');
        const overallScore = Math.round(
            (headlineResults.best_score * 0.4 + hookResults.best_engagement * 0.6) * 10
        ) / 10;
        recDiv.innerHTML = `
            <div><strong>Best Headline:</strong> ${headlineResults.winner}</div>
            <div><strong>Best Code Hook:</strong> ${hookResults.winner.substring(0, 100)}...</div>
            <div><strong>Combined Score:</strong> ${overallScore}/100</div>
        `;

        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
            document.getElementById('btn-generate-report').textContent = '📊 Generate Report';
        }
    }

    renderReport() {
        const report = this.state.report;
        const container = document.getElementById('report-container');
        container.innerHTML = '';

        // Destroy previous charts
        this.destroyAllCharts();

        // Summary chart
        const summaryData = {
            continue: report.continue_items.length,
            stop: report.stop_items.length,
            create: report.create_next.length
        };
        
        const chartCanvas = document.createElement('canvas');
        chartCanvas.id = 'chart-strategy-summary';
        chartCanvas.style.marginBottom = '2rem';
        
        // We'll create this after the container is updated
        setTimeout(() => {
            this.createBarChart(
                'chart-strategy-summary',
                Object.keys(summaryData),
                Object.values(summaryData),
                'Count',
                '#48c482'
            );
        }, 100);

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

    exportToGitHubIssues() {
        if (!this.state.report) {
            alert('Please generate a report first');
            return;
        }

        const report = this.state.report;
        let content = `# Editorial Strategy Report\n\n`;
        content += `Generated: ${new Date(report.report_date).toLocaleDateString()}\n`;
        content += `Period: ${report.period}\n\n`;
        content += `${report.summary}\n\n`;

        content += `## 📋 Continue Items\n`;
        report.continue_items.forEach(item => {
            content += `- [ ] ${item.topic || item} (${item.format || ''})\n`;
        });

        content += `\n## ⛔ Stop Items\n`;
        report.stop_items.forEach(item => {
            content += `- [ ] ${item.topic || item} (${item.format || ''})\n`;
        });

        content += `\n## ✨ Create Next\n`;
        report.create_next.forEach(item => {
            content += `- [ ] ${item.topic || item} (${item.format || ''})\n`;
        });

        navigator.clipboard.writeText(content).then(() => {
            alert('Report copied to clipboard! Paste it into a GitHub issue.');
        });
    }

    exportToPDF() {
        if (!this.state.report) {
            alert('Please generate a report first');
            return;
        }
        
        // Simple text-based export for now (can be enhanced with actual PDF library)
        const report = this.state.report;
        let content = `EDITORIAL STRATEGY REPORT\n`;
        content += `Generated: ${new Date(report.report_date).toLocaleDateString()}\n`;
        content += `Period: ${report.period}\n\n`;
        content += `${report.summary}\n\n`;

        content += `CONTINUE ITEMS\n`;
        report.continue_items.forEach(item => {
            content += `• ${item.topic || item} (${item.format || ''})\n`;
        });

        content += `\nSTOP ITEMS\n`;
        report.stop_items.forEach(item => {
            content += `• ${item.topic || item} (${item.format || ''})\n`;
        });

        content += `\nCREATE NEXT\n`;
        report.create_next.forEach(item => {
            content += `• ${item.topic || item} (${item.format || ''})\n`;
        });

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `strategy-report-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    renderTrace(containerId, trace) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        if (!trace || !trace.steps) return;

        trace.steps.forEach(step => {
            const entry = document.createElement('div');
            entry.className = 'trace-entry';
            entry.innerHTML = `
                <div class="trace-agent">${step.agent || 'System'}</div>
                <div class="trace-status ${step.status || 'success'}">${(step.status || 'success').toUpperCase()}</div>
                <div class="trace-detail">${step.message || ''}</div>
                <div class="trace-duration">${step.duration || '0ms'}</div>
            `;
            container.appendChild(entry);
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ContentPulseApp();
});
