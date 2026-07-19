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
        document.getElementById('btn-export-github').addEventListener('click', () => this.exportToGitHubIssues());

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
