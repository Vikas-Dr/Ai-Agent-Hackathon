// DevPulse App - Complete Functionality with Loading States

class DevPulseApp {
    constructor() {
        this.state = {
            topics: [],
            formats: [],
            audiences: [],
            charts: {},
            userContent: [],
            customData: []
        };
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadConfig();
        this.setupEventListeners();
    }

    // ==================== LOADING HELPER ====================

    showLoading(elementId, show = true) {
        const el = document.getElementById(elementId);
        if (!el) return;
        if (show) {
            el.innerHTML = '<div class="spinner">⏳ Loading...</div>';
        }
    }

    hideLoading(elementId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        el.innerHTML = '';
    }

    // ==================== NAVIGATION ====================

    setupNavigation() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.dataset.tab);
            });
        });
    }

    switchTab(tabName) {
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            }
        });
    }

    // ==================== CONFIG ====================

    async loadConfig() {
        try {
            const [topics, formats, audiences] = await Promise.all([
                fetch('/api/topics').then(r => r.json()),
                fetch('/api/formats').then(r => r.json()),
                fetch('/api/audiences').then(r => r.json())
            ]);

            this.state.topics = topics || [];
            this.state.formats = formats || [];
            this.state.audiences = audiences || [];

            this.populateSelects();
        } catch (e) {
            console.error('Failed to load config:', e);
        }
    }

    populateSelects() {
        this.populateSelect('scorer-topic', this.state.topics);
        this.populateSelect('scorer-format', this.state.formats);
        this.populateSelect('scorer-audience', this.state.audiences);
    }

    populateSelect(elementId, options) {
        const select = document.getElementById(elementId);
        if (!select) return;
        
        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt;
            select.appendChild(option);
        });
    }

    // ==================== EVENT LISTENERS ====================

    setupEventListeners() {
        // Dashboard
        document.getElementById('btn-run-analysis').addEventListener('click', () => this.runAnalysis());
        document.getElementById('data-input-form').addEventListener('submit', (e) => this.handleDataInput(e));
        document.getElementById('llm-form').addEventListener('submit', (e) => this.handleLLMRequest(e));

        // Scorer
        document.getElementById('scorer-form').addEventListener('submit', (e) => this.scoreContent(e));

        // A/B Tester
        document.getElementById('btn-ab-test').addEventListener('click', () => this.runABTest());

        // Custom Data
        document.getElementById('upload-zone').addEventListener('click', () => {
            document.getElementById('csv-file').click();
        });
        document.getElementById('csv-file').addEventListener('change', (e) => this.handleCSVSelect(e));
        document.getElementById('btn-analyze-custom').addEventListener('click', () => this.uploadCSV());
        document.getElementById('manual-data-form').addEventListener('submit', (e) => this.handleManualDataEntry(e));

        // Strategy
        document.getElementById('btn-generate-report').addEventListener('click', () => this.generateReport());

        // Data Table
        document.getElementById('btn-load-data').addEventListener('click', () => this.loadData());

        // Real-time preview
        document.getElementById('input-markdown').addEventListener('input', () => this.updatePreview());
        document.getElementById('input-title').addEventListener('input', () => this.updatePreview());
        document.getElementById('input-topic').addEventListener('input', () => this.updatePreview());
    }

    // ==================== DASHBOARD ====================

    async runAnalysis() {
        try {
            const btn = document.getElementById('btn-run-analysis');
            btn.disabled = true;
            btn.textContent = '⏳ Analyzing...';

            const response = await fetch('/api/report', { method: 'POST' });
            const result = await response.json();

            if (result.analysis) {
                const analysis = result.analysis;
                
                document.getElementById('metric-articles').textContent = '150';
                document.getElementById('metric-topics').textContent = analysis.top_topics.length;
                document.getElementById('metric-insights').textContent = analysis.insights.length;
                document.getElementById('metric-format').textContent = analysis.top_formats[0] || '-';

                const insightsList = document.getElementById('insights-list');
                insightsList.innerHTML = '';
                analysis.insights.forEach(insight => {
                    const li = document.createElement('li');
                    li.textContent = insight;
                    insightsList.appendChild(li);
                });

                this.drawTopicChart(analysis.top_topics);
            }
        } catch (e) {
            console.error('Analysis failed:', e);
            alert('❌ Analysis failed: ' + e.message);
        } finally {
            const btn = document.getElementById('btn-run-analysis');
            btn.disabled = false;
            btn.textContent = '🔄 Run Analysis';
        }
    }

    drawTopicChart(topics) {
        const ctx = document.getElementById('chart-topics');
        if (!ctx) return;

        if (this.state.charts.topics) {
            this.state.charts.topics.destroy();
        }

        const data = topics || ['API Design', 'Authentication', 'Backend', 'Frontend', 'DevOps'];
        const scores = [85, 78, 72, 65, 58];

        this.state.charts.topics = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data,
                datasets: [{
                    label: 'Performance Score',
                    data: scores,
                    backgroundColor: '#00d4ff',
                    borderColor: '#00a8cc',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#a0a0a0' }
                    }
                },
                scales: {
                    y: {
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2d3748' }
                    },
                    x: {
                        ticks: { color: '#a0a0a0' },
                        grid: { color: '#2d3748' }
                    }
                }
            }
        });
    }

    // ==================== DATA INPUT ====================

    handleDataInput(e) {
        e.preventDefault();

        const title = document.getElementById('input-title').value;
        const topic = document.getElementById('input-topic').value;
        const format = document.getElementById('input-format').value;
        const audience = document.getElementById('input-audience').value;
        const wordcount = document.getElementById('input-wordcount').value;
        const markdown = document.getElementById('input-markdown').value;

        if (!title || !topic || !format || !audience) {
            alert('❌ Please fill all fields');
            return;
        }

        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = '⏳ Adding...';

        const data = { title, topic, format, audience, wordcount, markdown };
        this.state.userContent.push(data);

        // Send to backend
        fetch('/api/add-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(r => r.json())
          .then(result => {
              if (result.success) {
                  alert('✅ ' + result.message);
                  this.updatePreview();
                  e.target.reset();
              }
          })
          .catch(err => alert('❌ Error: ' + err))
          .finally(() => {
              btn.disabled = false;
              btn.textContent = '📤 Add Content';
          });
    }

    updatePreview() {
        const title = document.getElementById('input-title').value || '(Title)';
        const topic = document.getElementById('input-topic').value || '(Topic)';
        const wordcount = document.getElementById('input-wordcount').value || '0';
        const markdown = document.getElementById('input-markdown').value || '(No content yet)';

        const preview = document.getElementById('preview-container');
        document.getElementById('preview-title').textContent = title;
        document.getElementById('preview-meta').textContent = `${topic} • ${wordcount} words`;
        document.getElementById('preview-content').textContent = markdown;

        if (title !== '(Title)' || markdown !== '(No content yet)') {
            preview.classList.remove('hidden');
        }
    }

    // ==================== LLM INTEGRATION ====================

    async handleLLMRequest(e) {
        e.preventDefault();

        const prompt = document.getElementById('llm-prompt').value;
        const type = document.getElementById('llm-type').value;
        const tone = document.getElementById('llm-tone').value;

        if (!prompt || !type || !tone) {
            alert('❌ Please fill all fields');
            return;
        }

        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = '⏳ Generating...';

        const resultsDiv = document.getElementById('llm-results');
        const outputDiv = document.getElementById('llm-output');
        
        outputDiv.innerHTML = '<p>🔄 Generating AI suggestions...</p>';
        resultsDiv.classList.remove('hidden');

        try {
            const response = await fetch('/api/llm-suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, type, tone })
            });

            const result = await response.json();
            if (result.success) {
                outputDiv.innerHTML = result.content;
            } else {
                outputDiv.innerHTML = '<p>❌ Error: ' + result.error + '</p>';
            }
        } catch (err) {
            outputDiv.innerHTML = '<p>❌ Error: ' + err + '</p>';
        } finally {
            btn.disabled = false;
            btn.textContent = '✨ Get Suggestions';
        }
    }

    // ==================== SCORER ====================

    async scoreContent(e) {
        e.preventDefault();

        const title = document.getElementById('scorer-title').value;
        const topic = document.getElementById('scorer-topic').value;
        const format = document.getElementById('scorer-format').value;
        const audience = document.getElementById('scorer-audience').value;
        const wordcount = document.getElementById('scorer-wordcount').value;
        const markdown = document.getElementById('scorer-markdown').value;

        if (!title || !topic || !format || !audience) {
            alert('❌ Please fill required fields');
            return;
        }

        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = '⏳ Scoring...';

        try {
            const response = await fetch('/api/score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title, topic, format, audience,
                    word_count: wordcount,
                    draft_markdown: markdown
                })
            });

            const result = await response.json();
            if (result.prediction) {
                const score = result.prediction.predicted_score;
                document.getElementById('result-score').textContent = score;
                document.getElementById('result-reasoning').textContent = result.prediction.reasoning;

                const suggestionsList = document.getElementById('result-suggestions');
                suggestionsList.innerHTML = '';
                result.prediction.suggestions.forEach(sug => {
                    const li = document.createElement('li');
                    li.textContent = sug;
                    suggestionsList.appendChild(li);
                });

                document.getElementById('score-result').classList.remove('hidden');
            }
        } catch (err) {
            alert('❌ Scoring failed: ' + err);
        } finally {
            btn.disabled = false;
            btn.textContent = '📈 Score This Draft';
        }
    }

    // ==================== A/B TESTER ====================

    async runABTest() {
        try {
            const btn = document.getElementById('btn-ab-test');
            btn.disabled = true;
            btn.textContent = '⏳ Testing...';

            const headlines = [
                document.querySelector('.ab-input').value,
                document.querySelectorAll('.ab-input')[1].value,
                document.querySelectorAll('.ab-input')[2].value
            ];

            const response = await fetch('/api/ab-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ headlines })
            });

            const result = await response.json();
            if (result.success) {
                let html = '<h3>📊 A/B Test Results</h3>';
                result.results.forEach((r, i) => {
                    const bg = i === result.results.findIndex(x => x.score === Math.max(...result.results.map(y => y.score))) ? '#1a4d26' : '#2d3748';
                    html += `<div style="background:${bg};padding:15px;margin:10px 0;border-radius:5px;"><strong>${r.headline}</strong><br>Score: ${r.score}/100</div>`;
                });
                html += `<h4 style="color:#00d4ff;margin-top:20px;">🏆 Winner: ${result.winner}</h4>`;
                document.getElementById('ab-results').innerHTML = html;
                document.getElementById('ab-results').classList.remove('hidden');
            }
        } catch (err) {
            alert('❌ A/B test failed: ' + err);
        } finally {
            const btn = document.getElementById('btn-ab-test');
            btn.disabled = false;
            btn.textContent = '🔀 Run A/B Test';
        }
    }

    // ==================== CUSTOM DATA ====================

    handleCSVSelect(e) {
        if (e.target.files.length > 0) {
            document.getElementById('btn-analyze-custom').classList.remove('hidden');
        }
    }

    async uploadCSV() {
        try {
            const file = document.getElementById('csv-file').files[0];
            if (!file) {
                alert('❌ Please select a file');
                return;
            }

            const btn = document.getElementById('btn-analyze-custom');
            btn.disabled = true;
            btn.textContent = '⏳ Uploading...';

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/upload-csv', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                alert('✅ ' + result.message);
                this.loadData();
            } else {
                alert('❌ ' + result.error);
            }
        } catch (err) {
            alert('❌ Upload failed: ' + err);
        } finally {
            const btn = document.getElementById('btn-analyze-custom');
            btn.disabled = false;
            btn.textContent = '🚀 Analyze';
        }
    }

    handleManualDataEntry(e) {
        e.preventDefault();

        const title = document.getElementById('manual-title').value;
        const topic = document.getElementById('manual-topic').value;
        const format = document.getElementById('manual-format').value;
        const views = document.getElementById('manual-views').value;
        const score = document.getElementById('manual-score').value;

        if (!title || !topic || !format) {
            alert('❌ Please fill required fields');
            return;
        }

        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = '⏳ Adding...';

        const data = { title, topic, format, views: parseInt(views), score: parseInt(score) };
        
        fetch('/api/add-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(r => r.json())
          .then(result => {
              if (result.success) {
                  alert('✅ Data entry added');
                  this.addToCustomTable(data);
                  e.target.reset();
              }
          })
          .catch(err => alert('❌ Error: ' + err))
          .finally(() => {
              btn.disabled = false;
              btn.textContent = '➕ Add Entry';
          });
    }

    addToCustomTable(row) {
        const tbody = document.getElementById('custom-table-body');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.title}</td>
            <td>${row.topic}</td>
            <td>${row.format}</td>
            <td>${row.views || 0}</td>
            <td>${row.score || 75}</td>
        `;
        tbody.appendChild(tr);
    }

    // ==================== STRATEGY ====================

    async generateReport() {
        try {
            const btn = document.getElementById('btn-generate-report');
            btn.disabled = true;
            btn.textContent = '⏳ Generating...';

            const response = await fetch('/api/report', { method: 'POST' });
            const result = await response.json();

            if (result.report) {
                const report = result.report;
                let html = '<div class="report-card" style="background:#1a1f26;border:1px solid #2d3748;padding:20px;border-radius:8px;margin-top:20px;">';
                html += '<h3 style="color:#00d4ff;margin-bottom:15px;">📊 Strategic Recommendations</h3>';
                
                if (report.summary) {
                    html += `<p style="margin-bottom:20px;">${report.summary}</p>`;
                }
                
                if (report.create_next) {
                    html += '<h4 style="margin-top:20px;margin-bottom:10px;">📝 Topics to Create:</h4><ul>';
                    report.create_next.forEach(item => {
                        const color = item.priority === 'high' ? '#ff6b6b' : item.priority === 'medium' ? '#ffd93d' : '#6bcf7f';
                        html += `<li style="margin:8px 0;color:#e0e0e0;"><span style="color:${color};font-weight:bold;">[${item.priority.toUpperCase()}]</span> ${item.topic}</li>`;
                    });
                    html += '</ul>';
                }
                
                html += '</div>';
                document.getElementById('report-content').innerHTML = html;
            }
        } catch (err) {
            alert('❌ Report generation failed: ' + err);
        } finally {
            const btn = document.getElementById('btn-generate-report');
            btn.disabled = false;
            btn.textContent = '📊 Generate Report';
        }
    }

    // ==================== DATA TABLE ====================

    async loadData() {
        try {
            const btn = document.getElementById('btn-load-data');
            btn.disabled = true;
            btn.textContent = '⏳ Loading...';

            const response = await fetch('/api/data?limit=20&offset=0');
            const result = await response.json();

            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            if (result.rows && result.rows.length > 0) {
                result.rows.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${row.title}</td>
                        <td>${row.topic}</td>
                        <td>${row.format}</td>
                        <td>${row.views || 0}</td>
                        <td>${row.performance_score || 75}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#a0a0a0;">No data available</td></tr>';
            }
        } catch (err) {
            alert('❌ Data loading failed: ' + err);
        } finally {
            const btn = document.getElementById('btn-load-data');
            btn.disabled = false;
            btn.textContent = '🔄 Load Data';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new DevPulseApp();
});
