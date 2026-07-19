// DevPulse App - Clean Frontend Controller

class DevPulseApp {
    constructor() {
        this.state = {
            topics: [],
            formats: [],
            audiences: [],
            charts: {},
            userContent: []
        };
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadConfig().then(() => {
            // Load initial dashboard metrics and database
            this.runAnalysis(true); 
            this.loadData();
        });
        this.setupEventListeners();
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
        const targetPane = document.getElementById(tabName);
        if (targetPane) {
            targetPane.classList.add('active');
        }

        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            }
        });

        // Auto-refresh lists when switching tabs
        if (tabName === 'datatable') {
            this.loadData();
        }
    }

    // ==================== CONFIG SELECTION BOOTSTRAP ====================

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
            console.error('Failed to load system configs:', e);
        }
    }

    populateSelects() {
        // Scorer selects
        this.populateSelect('scorer-topic', this.state.topics);
        this.populateSelect('scorer-format', this.state.formats);
        this.populateSelect('scorer-audience', this.state.audiences);

        // Manual Data select dropdowns
        this.populateSelect('manual-topic-select', this.state.topics);
        this.populateSelect('manual-format-select', this.state.formats);
        this.populateSelect('manual-audience-select', this.state.audiences);
    }

    populateSelect(elementId, options) {
        const select = document.getElementById(elementId);
        if (!select) return;
        
        // Clear any existing options except the first placeholder
        const firstOption = select.options[0];
        select.innerHTML = '';
        if (firstOption) {
            select.appendChild(firstOption);
        }

        options.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()); // Clean labels
            select.appendChild(option);
        });
    }

    // ==================== EVENT REGISTRATION ====================

    setupEventListeners() {
        // Run Analysis button on dashboard
        const runAnalysisBtn = document.getElementById('btn-run-analysis');
        if (runAnalysisBtn) {
            runAnalysisBtn.addEventListener('click', () => this.runAnalysis());
        }

        // Form submission for Scorer
        const scorerForm = document.getElementById('scorer-form');
        if (scorerForm) {
            scorerForm.addEventListener('submit', (e) => this.scoreContent(e));
        }

        // CSV Upload interactions
        const uploadZone = document.getElementById('upload-zone');
        if (uploadZone) {
            uploadZone.addEventListener('click', () => {
                document.getElementById('csv-file').click();
            });
        }
        const csvFile = document.getElementById('csv-file');
        if (csvFile) {
            csvFile.addEventListener('change', (e) => this.handleCSVSelect(e));
        }
        const analyzeCustomBtn = document.getElementById('btn-analyze-custom');
        if (analyzeCustomBtn) {
            analyzeCustomBtn.addEventListener('click', () => this.uploadCSV());
        }

        // Manual Data Ingestion Form
        const manualForm = document.getElementById('manual-data-form');
        if (manualForm) {
            manualForm.addEventListener('submit', (e) => this.handleManualDataEntry(e));
        }

        // Strategy report execution
        const reportBtn = document.getElementById('btn-generate-report');
        if (reportBtn) {
            reportBtn.addEventListener('click', () => this.generateReport());
        }

        // Refresh Data Database Button
        const loadDataBtn = document.getElementById('btn-load-data');
        if (loadDataBtn) {
            loadDataBtn.addEventListener('click', () => this.loadData());
        }

        // A/B Tester button
        const abBtn = document.getElementById('btn-ab-test');
        if (abBtn) {
            abBtn.addEventListener('click', () => this.runABTest());
        }
    }

    // ==================== DASHBOARD & REAL PIPELINE ANALYSIS ====================

    async runAnalysis(silent = false) {
        const btn = document.getElementById('btn-run-analysis');
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ Run Analysis...';
        }

        try {
            const response = await fetch('/api/report', { method: 'POST' });
            const result = await response.json();

            if (result.analysis) {
                const analysis = result.analysis;
                
                // Update UI metric counters dynamically
                const totalArticles = result.trace && result.trace.entries && result.trace.entries[0]
                    ? parseInt(result.trace.entries[0].output_summary.split(' ')[0]) || 0 
                    : 0;

                document.getElementById('metric-articles').textContent = totalArticles || this.state.userContent.length || '200';
                document.getElementById('metric-topics').textContent = analysis.top_topics ? analysis.top_topics.length : '0';
                document.getElementById('metric-insights').textContent = analysis.insights ? analysis.insights.length : '0';
                
                const topFormatObj = analysis.top_formats && analysis.top_formats.length > 0
                    ? analysis.top_formats[0]
                    : '-';
                const topFormatStr = typeof topFormatObj === 'string' 
                    ? topFormatObj 
                    : (topFormatObj && topFormatObj.format ? topFormatObj.format : '-');
                document.getElementById('metric-format').textContent = topFormatStr.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

                // Populate Insights listing card
                const insightsList = document.getElementById('insights-list');
                insightsList.innerHTML = '';
                if (analysis.insights && analysis.insights.length > 0) {
                    analysis.insights.forEach(insight => {
                        const li = document.createElement('li');
                        li.textContent = insight;
                        insightsList.appendChild(li);
                    });
                } else {
                    insightsList.innerHTML = '<li class="empty-state-text">No insights generated yet.</li>';
                }

                // Render dynamic Performance Chart based on updated data
                this.drawTopicChart(analysis.top_topics);
                
                if (!silent) {
                    this.showToast('✅ Analysis complete! Performance charts updated.', 'success');
                }
            }
        } catch (e) {
            console.error('Analysis execution failed:', e);
            if (!silent) {
                this.showToast('❌ Analysis failed: ' + e.message, 'error');
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '🔄 Run Analysis';
            }
        }
    }

    drawTopicChart(topics) {
        const ctx = document.getElementById('chart-topics');
        if (!ctx) return;

        if (this.state.charts.topics) {
            this.state.charts.topics.destroy();
        }

        // Fallback default topics if none found
        let labels = [];
        let scores = [];

        if (topics && topics.length > 0) {
            labels = topics.map(t => t.topic);
            scores = topics.map(t => t.avg_score || t.performance_score);
        } else {
            labels = ['API Design', 'Authentication', 'Cloud Infrastructure', 'Database & Data', 'DevOps & CI/CD'];
            scores = [85, 78, 72, 65, 58];
        }

        this.state.charts.topics = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Performance Score (0-100)',
                    data: scores,
                    backgroundColor: 'rgba(0, 212, 255, 0.45)',
                    borderColor: '#00d4ff',
                    borderWidth: 2,
                    borderRadius: 6,
                    hoverBackgroundColor: 'rgba(0, 255, 212, 0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } },
                        grid: { color: '#242f3d' }
                    },
                    x: {
                        ticks: { color: '#94a3b8' },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // ==================== DRAFT PERFORMANCE SCORER ====================

    async scoreContent(e) {
        e.preventDefault();

        const title = document.getElementById('scorer-title').value;
        const topic = document.getElementById('scorer-topic').value;
        const format = document.getElementById('scorer-format').value;
        const audience = document.getElementById('scorer-audience').value;
        const wordcount = document.getElementById('scorer-wordcount').value;
        const markdown = document.getElementById('scorer-markdown').value;
        const assetFile = document.getElementById('scorer-asset').files[0];

        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = '⏳ Evaluating Draft...';

        try {
            let response;
            if (assetFile) {
                // Use FormData for file upload
                const formData = new FormData();
                formData.append('title', title);
                formData.append('topic', topic);
                formData.append('format', format);
                formData.append('audience', audience);
                formData.append('word_count', parseInt(wordcount));
                formData.append('draft_markdown', markdown);
                formData.append('asset', assetFile);

                response = await fetch('/api/score', {
                    method: 'POST',
                    body: formData
                });
            } else {
                // Standard JSON request
                response = await fetch('/api/score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title, topic, format, audience,
                        word_count: parseInt(wordcount),
                        draft_markdown: markdown
                    })
                });
            }

            const result = await response.json();
            if (result.prediction) {
                const score = result.prediction.predicted_score;
                document.getElementById('result-score').textContent = score;
                document.getElementById('result-reasoning').textContent = result.prediction.reasoning;

                // Color code the circle border dynamically
                const circle = document.querySelector('.score-circle');
                if (circle) {
                    if (score >= 75) {
                        circle.style.borderColor = '#00ffd4';
                    } else if (score >= 50) {
                        circle.style.borderColor = '#ffd93d';
                    } else {
                        circle.style.borderColor = '#ff6b6b';
                    }
                }

                // Render suggestions list
                const suggestionsList = document.getElementById('result-suggestions');
                suggestionsList.innerHTML = '';
                result.prediction.suggestions.forEach(sug => {
                    const li = document.createElement('li');
                    li.textContent = sug;
                    suggestionsList.appendChild(li);
                });

                document.getElementById('score-result').classList.remove('hidden');
                this.showToast('🎯 Score calculated successfully!', 'success');
            } else if (result.error) {
                this.showToast('❌ Predictor failed: ' + result.error, 'error');
            }
        } catch (err) {
            this.showToast('❌ Scoring failed: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '📈 Score This Draft';
        }
    }

    // ==================== A/B PERFORMANCE TESTER ====================

    async runABTest() {
        const btn = document.getElementById('btn-ab-test');
        if (!btn) return;
        btn.disabled = true;
        btn.textContent = '⏳ Calculating...';

        const headlines = [
            document.getElementById('ab-headline-1').value,
            document.getElementById('ab-headline-2').value,
            document.getElementById('ab-headline-3').value
        ].filter(h => h.trim() !== '');

        if (headlines.length < 2) {
            this.showToast('❌ Please enter at least 2 variants.', 'error');
            btn.disabled = false;
            btn.textContent = '🔀 Run A/B Performance Test';
            return;
        }

        try {
            const response = await fetch('/api/ab-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ headlines })
            });

            const result = await response.json();
            if (result.success) {
                let html = '<div style="display:flex; flex-direction:column; gap:16px; margin-top:16px;">';
                result.results.forEach(r => {
                    const isWinner = r.headline === result.winner;
                    const borderStyle = isWinner ? 'border: 2px solid var(--accent);' : 'border: 1px solid var(--border-color);';
                    const glowClass = isWinner ? 'box-shadow: var(--glow-shadow);' : '';
                    html += `
                        <div style="background:var(--bg-primary); padding:16px; border-radius:10px; ${borderStyle} ${glowClass} display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:700; color:#fff;">${r.headline}</div>
                                <div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">Estimated conversions & engagement performance</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:24px; font-weight:800; color:${isWinner ? 'var(--accent)' : 'var(--text-secondary)'}; font-family:'JetBrains Mono';">${r.score}/100</div>
                                ${isWinner ? '<span style="font-size:11px; color:#00ffd4; font-weight:700; text-transform:uppercase;">🏆 Top Performer</span>' : ''}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                document.getElementById('ab-results-list').innerHTML = html;
                document.getElementById('ab-results').classList.remove('hidden');
                this.showToast('📈 A/B test complete!', 'success');
            } else {
                this.showToast('❌ Testing failed: ' + result.error, 'error');
            }
        } catch (err) {
            this.showToast('❌ Testing error: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '🔀 Run A/B Performance Test';
        }
    }

    // ==================== MANUAL DATA ENTRY & FILE UPLOAD ====================

    async handleManualDataEntry(e) {
        e.preventDefault();

        const title = document.getElementById('manual-title').value;
        const topic = document.getElementById('manual-topic-select').value;
        const format = document.getElementById('manual-format-select').value;
        const audience = document.getElementById('manual-audience-select').value;
        const wordcount = document.getElementById('manual-wordcount').value;
        const views = document.getElementById('manual-views').value;
        const conversions = document.getElementById('manual-conversions').value;

        const btn = e.target.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = '⏳ Adding Entry...';

        const data = {
            title, topic, format, audience,
            wordcount: parseInt(wordcount),
            views: parseInt(views),
            conversions: parseInt(conversions),
            score: 75 // default starting score
        };
        
        try {
            const response = await fetch('/api/add-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            
            if (result.success) {
                this.showToast('✅ Data entry added successfully!', 'success');
                e.target.reset();
                this.loadData();
                this.runAnalysis(true); // silent dashboard update
            } else {
                this.showToast('❌ Error adding data: ' + result.error, 'error');
            }
        } catch (err) {
            this.showToast('❌ Error adding data: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '➕ Add Entry';
        }
    }

    handleCSVSelect(e) {
        const analyzeBtn = document.getElementById('btn-analyze-custom');
        const uploadZone = document.getElementById('upload-zone');
        if (e.target.files.length > 0) {
            if (analyzeBtn) analyzeBtn.classList.remove('hidden');
            if (uploadZone) {
                uploadZone.style.borderColor = 'var(--accent)';
                uploadZone.querySelector('p').textContent = `✓ Selected: ${e.target.files[0].name}`;
            }
        }
    }

    async uploadCSV() {
        const file = document.getElementById('csv-file').files[0];
        if (!file) {
            this.showToast('❌ Please select a CSV file first.', 'error');
            return;
        }

        const btn = document.getElementById('btn-analyze-custom');
        btn.disabled = true;
        btn.textContent = '⏳ Ingesting CSV...';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload-csv', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                this.showToast(result.message, 'success');
                this.loadData();
                this.runAnalysis(true); // update dashboard silently
                
                // Reset upload state
                document.getElementById('csv-file').value = '';
                btn.classList.add('hidden');
                document.getElementById('upload-zone').querySelector('p').textContent = 'Drag and drop your performance CSV file here, or click to browse';
                document.getElementById('upload-zone').style.borderColor = 'var(--border-color)';
            } else {
                this.showToast('❌ Upload failed: ' + result.error, 'error');
            }
        } catch (err) {
            this.showToast('❌ Ingestion failed: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '🚀 Load and Parse File';
        }
    }

    // ==================== STRATEGY REPORT FLOW ====================

    async generateReport() {
        const btn = document.getElementById('btn-generate-report');
        btn.disabled = true;
        btn.textContent = '⏳ Generating Report...';

        try {
            const response = await fetch('/api/report', { method: 'POST' });
            const result = await response.json();

            if (result.report) {
                const report = result.report;
                let html = '<div class="report-card">';
                html += '<h3>🎯 Content Strategy Recommendations</h3>';
                
                if (report.summary) {
                    html += `<p style="margin-bottom: 24px; color: var(--text-primary); font-size: 15px; line-height: 1.6;">${report.summary}</p>`;
                }
                
                // Render CONTINUE items
                if (report.continue_items && report.continue_items.length > 0) {
                    html += '<h4 style="color: #00ffd4; margin-top: 20px; margin-bottom: 12px;">✅ What to Continue:</h4><ul>';
                    report.continue_items.forEach(item => {
                        const fmtName = (item.format || 'tutorial').replace(/_/g, ' ');
                        html += `<li style="margin: 8px 0 8px 16px; color: var(--text-primary);"><strong style="color:#fff;">${item.topic} (${fmtName})</strong>: ${item.reason}</li>`;
                    });
                    html += '</ul>';
                }

                // Render STOP items
                if (report.stop_items && report.stop_items.length > 0) {
                    html += '<h4 style="color: #ff6b6b; margin-top: 20px; margin-bottom: 12px;">🛑 What to Stop / Reallocate:</h4><ul>';
                    report.stop_items.forEach(item => {
                        const fmtName = (item.format || 'technical_blog').replace(/_/g, ' ');
                        html += `<li style="margin: 8px 0 8px 16px; color: var(--text-primary);"><strong style="color:#fff;">${item.topic} (${fmtName})</strong>: ${item.reason}</li>`;
                    });
                    html += '</ul>';
                }

                // Render CREATE NEXT items (Gaps)
                if (report.create_next && report.create_next.length > 0) {
                    html += '<h4 style="color: var(--accent); margin-top: 20px; margin-bottom: 12px;">🚀 Content Gaps & Gaps to Create Next:</h4><ul>';
                    report.create_next.forEach(item => {
                        const fmtName = (item.suggested_format || item.format || 'tutorial').replace(/_/g, ' ');
                        html += `<li style="margin: 8px 0 8px 16px; color: var(--text-primary);"><strong style="color:#fff;">${item.topic}</strong> (Target: ${item.target_audience || 'developers'}, Recommended format: ${fmtName}): ${item.reasoning}</li>`;
                    });
                    html += '</ul>';
                }

                // Render Execution trace timeline dynamically
                if (result.trace && result.trace.entries) {
                    html += '<div class="trace-timeline">';
                    html += '<h4 style="color: var(--text-secondary); margin-bottom: 16px; font-size:14px; text-transform:uppercase;">📝 Multi-Agent Trace Log:</h4>';
                    result.trace.entries.forEach(step => {
                        const icon = step.status === 'success' ? '✅' : '❌';
                        html += `
                            <div class="trace-step">
                                <span style="font-weight: 700; color:#fff;">[${step.agent}]</span> 
                                <span style="color:${step.status === 'success' ? '#00ffd4' : '#ff6b6b'}; font-size:12px;">${icon} ${step.status.toUpperCase()}</span>
                                <span style="color: var(--text-secondary); font-size:12px;"> (${step.duration_seconds.toFixed(3)}s)</span>
                                <div style="color: var(--text-secondary); font-size: 12px; margin-top: 4px;">In: ${step.input_summary} | Out: ${step.output_summary}</div>
                            </div>
                        `;
                    });
                    html += '</div>';
                }
                
                html += '</div>';
                document.getElementById('report-content').innerHTML = html;
                this.showToast('📋 Strategy report compiled successfully!', 'success');
            }
        } catch (err) {
            this.showToast('❌ Report generation failed: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '📊 Generate Strategy Report';
        }
    }

    // ==================== DATA DATABASE VIEW ====================

    async loadData() {
        const btn = document.getElementById('btn-load-data');
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ Loading...';
        }

        try {
            const response = await fetch('/api/data?limit=25&offset=0');
            const result = await response.json();

            const tbody = document.getElementById('table-body');
            if (tbody) {
                tbody.innerHTML = '';

                if (result.rows && result.rows.length > 0) {
                    result.rows.forEach(row => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td style="font-weight:600; color:#fff;">${row.title}</td>
                            <td><span class="header-badge" style="border:none; padding:2px 8px; font-size:11px;">${row.topic}</span></td>
                            <td>${row.format.replace(/_/g, ' ')}</td>
                            <td>${row.audience_segment || row.audience || 'developers'}</td>
                            <td style="font-family:'JetBrains Mono';">${row.word_count || row.wordcount || 1500}</td>
                            <td style="font-family:'JetBrains Mono'; color:var(--accent); font-weight:600;">${(row.views || 0).toLocaleString()}</td>
                            <td style="font-family:'JetBrains Mono'; font-weight:700; color:${row.performance_score >= 75 ? '#00ffd4' : row.performance_score >= 50 ? '#ffd93d' : '#ff6b6b'}">${row.performance_score || 75}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                } else {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#a0a0a0;">No content performance data found in database.</td></tr>';
                }
            }
        } catch (err) {
            this.showToast('❌ Database load failed: ' + err.message, 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '🔄 Refresh Content Database';
            }
        }
    }

    // ==================== UI TOAST NOTIFICATION ====================

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.position = 'fixed';
        toast.style.bottom = '24px';
        toast.style.right = '24px';
        toast.style.padding = '14px 24px';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
        toast.style.zIndex = '9999';
        toast.style.fontSize = '14px';
        toast.style.fontWeight = '600';
        toast.style.transition = 'all 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';

        if (type === 'success') {
            toast.style.backgroundColor = '#13221b';
            toast.style.border = '1px solid #00ffd4';
            toast.style.color = '#00ffd4';
        } else {
            toast.style.backgroundColor = '#2c1318';
            toast.style.border = '1px solid #ff6b6b';
            toast.style.color = '#ff6b6b';
        }

        document.body.appendChild(toast);
        toast.textContent = message;

        // Force reflow
        toast.offsetHeight;

        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3500);
    }
}

// Instantiate on DOM load
document.addEventListener('DOMContentLoaded', () => {
    new DevPulseApp();
});
