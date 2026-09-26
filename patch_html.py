import re

with open("d:/passwordproject/index.html", "r") as f:
    content = f.read()

# Add CSS for comparison
css_addition = """
        /* Comparison Section */
        #comparison-section {
            display: none;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
            border-top: 1px solid var(--border-color);
            padding-top: 25px;
            opacity: 0;
            transition: opacity 0.5s ease;
        }

        #comparison-section.show {
            display: flex;
            opacity: 1;
        }

        .comparison-cards-container {
            display: flex;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .comparison-cards-container {
                flex-direction: column;
            }
        }

        .comparison-card {
            flex: 1;
            background-color: rgba(0, 0, 0, 0.3);
            border: 2px solid;
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .comparison-card.original {
            border-color: var(--color-weak);
        }

        .comparison-card.improved {
            border-color: var(--color-very-strong);
        }

        .comparison-header {
            font-size: 1.25rem;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
        }

        .comparison-card.original .comparison-header {
            color: var(--color-weak);
        }

        .comparison-card.improved .comparison-header {
            color: var(--color-very-strong);
        }

        .comp-pwd-display {
            font-size: 1.5rem;
            font-family: monospace;
            text-align: center;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            word-break: break-all;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .comp-stats {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .comp-stat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.95rem;
        }

        .comp-score {
            font-size: 1.5rem;
            font-weight: bold;
        }

        .improvement-banner {
            background-color: rgba(34, 197, 94, 0.1);
            border: 1px solid var(--color-very-strong);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            color: var(--color-very-strong);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .improvement-banner-title {
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .improvement-banner-stats {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 10px;
        }

        /* Score Comparison Bars */
        .score-comp-bars {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 10px;
        }
        
        .score-comp-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .score-comp-label {
            width: 80px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        
        .score-comp-bar-container {
            flex-grow: 1;
            height: 12px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }
        
        .score-comp-bar {
            height: 100%;
            width: 0%;
            transition: width 1s ease-out;
            border-radius: 6px;
        }
        
        .score-comp-value {
            width: 40px;
            text-align: right;
            font-size: 0.85rem;
            font-weight: bold;
        }

        .btn-improve {
            background-color: var(--accent-green);
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: bold;
            transition: all 0.2s;
            display: none; /* hidden initially */
            margin: 20px auto 0;
            width: fit-content;
        }
        
        .btn-improve:hover {
            background-color: var(--accent-green-hover);
            transform: translateY(-2px);
        }

        .btn-improve.loading {
            opacity: 0.7;
            pointer-events: none;
        }

        .comp-actions {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 15px;
        }
        
        .attack-comp-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
            font-size: 0.85rem;
        }
        
        .attack-comp-col {
            background: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
"""
content = content.replace("</style>", css_addition + "\n    </style>")

# Replace existing metrics-grid and details-grid closing tags
# Find <div class="section-card"> \h3 Suggestions => we insert btn-improve above it
btn_html = """            <button class="btn-improve" id="btn-improve">⚡ Show Me Strong Version</button>

            <!-- Comparison Section -->
            <div id="comparison-section">
                
                <div class="improvement-banner" id="imp-banner">
                    <div class="improvement-banner-title" id="imp-msg">Your password became significantly stronger!</div>
                    <div class="improvement-banner-stats">
                        <span id="imp-score">Score: +0</span>
                        <span id="imp-entropy">Entropy: +0 bits</span>
                        <span id="imp-time">Time: -</span>
                    </div>
                </div>

                <div class="score-comp-bars">
                    <div class="score-comp-row">
                        <div class="score-comp-label">Original</div>
                        <div class="score-comp-bar-container">
                            <div class="score-comp-bar" id="bar-orig" style="background-color: var(--color-weak)"></div>
                        </div>
                        <div class="score-comp-value" id="bar-orig-val">0</div>
                    </div>
                    <div class="score-comp-row">
                        <div class="score-comp-label">Improved</div>
                        <div class="score-comp-bar-container">
                            <div class="score-comp-bar" id="bar-imp" style="background-color: var(--color-very-strong)"></div>
                        </div>
                        <div class="score-comp-value" id="bar-imp-val">0</div>
                    </div>
                </div>

                <div class="comparison-cards-container">
                    <!-- Original Card -->
                    <div class="comparison-card original">
                        <div class="comparison-header">Your Password</div>
                        <div class="comp-pwd-display" id="comp-orig-pwd">****</div>
                        
                        <div class="comp-stats">
                            <div class="comp-stat-row">
                                <span>Score</span>
                                <span class="comp-score" style="color: var(--color-weak)" id="comp-orig-score">0/100</span>
                            </div>
                            <div class="comp-stat-row">
                                <span>Strength</span>
                                <span class="strength-badge" style="background: rgba(239,68,68,0.2); color: var(--color-weak)" id="comp-orig-str">WEAK</span>
                            </div>
                            <div class="comp-stat-row">
                                <span>Crack Time</span>
                                <span style="color: var(--color-weak)" id="comp-orig-time">-</span>
                            </div>
                            <div class="comp-stat-row">
                                <span>Entropy</span>
                                <span style="color: var(--color-weak)" id="comp-orig-ent">-</span>
                            </div>
                        </div>

                        <div style="margin-top: 10px;">
                            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 5px;">Top Vulnerabilities:</div>
                            <ul class="vuln-list" id="comp-orig-vulns" style="font-size: 0.85rem;"></ul>
                        </div>
                    </div>

                    <!-- Improved Card -->
                    <div class="comparison-card improved">
                        <div class="comparison-header">Stronger Version</div>
                        <div class="comp-pwd-display">
                            <span id="comp-imp-pwd"></span>
                            <button class="icon-btn" id="comp-copy-btn" title="Copy">📋</button>
                        </div>
                        
                        <div class="comp-stats">
                            <div class="comp-stat-row">
                                <span>Score</span>
                                <span class="comp-score" style="color: var(--color-very-strong)" id="comp-imp-score">0/100</span>
                            </div>
                            <div class="comp-stat-row">
                                <span>Strength</span>
                                <span class="strength-badge" style="background: rgba(34,197,94,0.2); color: var(--color-very-strong)" id="comp-imp-str">VERY STRONG</span>
                            </div>
                            <div class="comp-stat-row">
                                <span>Crack Time</span>
                                <span style="color: var(--color-very-strong)" id="comp-imp-time">-</span>
                            </div>
                            <div class="comp-stat-row">
                                <span>Entropy</span>
                                <span style="color: var(--color-very-strong)" id="comp-imp-ent">-</span>
                            </div>
                        </div>

                        <div style="margin-top: 10px;">
                            <div style="font-size: 0.85rem; color: var(--color-very-strong); margin-bottom: 5px;" id="comp-imp-vulns">
                                ✅ No vulnerabilities detected
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section-card" style="margin-top: 10px;">
                    <div style="font-size: 1.1rem; text-align: center; margin-bottom: 15px;">Attack Simulation Changes</div>
                    <div class="attack-comp-grid" id="comp-attack-grid"></div>
                </div>

                <div class="comp-actions">
                    <button class="btn btn-primary" id="btn-use-pwd">✅ Use This Password</button>
                    <button class="btn" id="btn-regen-pwd">🔄 Generate Another</button>
                </div>
            </div>"""

content = content.replace("""<div class="section-card">
                <h3 class="section-title">💡 Suggestions</h3>""", btn_html + """\n\n            <div class="section-card">
                <h3 class="section-title">💡 Suggestions</h3>""")

js_addition = """
        // --- COMPARISON LOGIC ---
        const IMPROVE_URL = 'http://localhost:5001/improve';
        const btnImprove = document.getElementById('btn-improve');
        const compSection = document.getElementById('comparison-section');
        const btnUsePwd = document.getElementById('btn-use-pwd');
        const btnRegenPwd = document.getElementById('btn-regen-pwd');
        const compCopyBtn = document.getElementById('comp-copy-btn');
        let currentImprovedPwd = '';

        btnImprove.addEventListener('click', () => {
            fetchImprove();
        });

        btnRegenPwd.addEventListener('click', () => {
            fetchImprove();
        });

        btnUsePwd.addEventListener('click', () => {
            if (currentImprovedPwd) {
                pwdInput.value = currentImprovedPwd;
                compSection.classList.remove('show');
                btnImprove.style.display = 'block';
                pwdInput.dispatchEvent(new Event('input'));
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });

        compCopyBtn.addEventListener('click', () => {
            if (currentImprovedPwd) {
                navigator.clipboard.writeText(currentImprovedPwd).then(() => {
                    const orig = compCopyBtn.innerHTML;
                    compCopyBtn.innerHTML = '✅';
                    setTimeout(() => compCopyBtn.innerHTML = orig, 2000);
                });
            }
        });

        async function fetchImprove() {
            const pwd = pwdInput.value;
            if (!pwd) return;

            btnImprove.classList.add('loading');
            btnImprove.textContent = "Generating stronger version...";
            
            try {
                const response = await fetch(IMPROVE_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: pwd })
                });

                if (!response.ok) throw new Error("Improvement failed");
                const data = await response.json();
                renderComparison(data);
                
                compSection.classList.add('show');
                btnImprove.style.display = 'none'; // hide button while showing comparison
                
            } catch (error) {
                console.error(error);
                alert("Failed to generate improved password.");
            } finally {
                btnImprove.classList.remove('loading');
                btnImprove.textContent = "⚡ Show Me Strong Version";
            }
        }

        function maskPassword(pwd) {
            if (!pwd) return "";
            if (pwd.length <= 4) return pwd[0] + "****";
            return pwd.substring(0, 4) + "****";
        }

        function renderComparison(data) {
            const orig = data.original;
            const imp = data.improved;
            const improvement = data.improvement;

            currentImprovedPwd = imp.password;

            // Banners
            document.getElementById('imp-msg').textContent = improvement.message;
            document.getElementById('imp-score').textContent = `Score improved by +${improvement.score_increase} points!`;
            document.getElementById('imp-entropy').textContent = `Entropy increased by +${improvement.entropy_increase} bits`;
            document.getElementById('imp-time').textContent = `Crack time: ${improvement.time_increase}`;

            // Bars
            setTimeout(() => {
                document.getElementById('bar-orig').style.width = `${orig.score}%`;
                document.getElementById('bar-imp').style.width = `${imp.score}%`;
            }, 100);
            document.getElementById('bar-orig-val').textContent = orig.score;
            document.getElementById('bar-imp-val').textContent = imp.score;

            // Original Card
            document.getElementById('comp-orig-pwd').textContent = maskPassword(orig.password);
            document.getElementById('comp-orig-score').textContent = `${orig.score}/100`;
            document.getElementById('comp-orig-str').textContent = orig.strength_level.toUpperCase();
            document.getElementById('comp-orig-time').textContent = orig.estimated_crack_time_readable;
            document.getElementById('comp-orig-ent').textContent = `${Math.round(orig.entropy_bits)} bits`;
            
            let origVulnsHtml = '';
            const origV = orig.vulnerability_types || [];
            origV.slice(0, 3).forEach(v => {
                origVulnsHtml += `<li class="vuln-item danger" style="padding: 2px 0;">❌ <span>${v}</span></li>`;
            });
            document.getElementById('comp-orig-vulns').innerHTML = origVulnsHtml;

            // Improved Card
            document.getElementById('comp-imp-pwd').textContent = imp.password;
            document.getElementById('comp-imp-score').textContent = `${imp.score}/100`;
            document.getElementById('comp-imp-str').textContent = imp.strength_level.toUpperCase();
            document.getElementById('comp-imp-time').textContent = imp.estimated_crack_time_readable;
            document.getElementById('comp-imp-ent').textContent = `${Math.round(imp.entropy_bits)} bits`;

            // Attack comparison grid
            const attackMap = {
                'dictionary': 'Dictionary', 'hybrid': 'Hybrid', 'keyboard': 'Keyboard',
                'sequential': 'Sequential', 'reverse': 'Reverse Seq', 'repeated': 'Repeated Char',
                'leetspeak': 'Leetspeak', 'date_based': 'Date Pattern', 'repeated_block': 'Repeated Block'
            };
            let gridHtml = '';
            for (const key in attackMap) {
                const name = attackMap[key];
                const oVuln = orig.attack_summary[key];
                const iVuln = imp.attack_summary[key];
                
                gridHtml += `
                <div class="attack-comp-col">
                    <div style="font-weight: bold; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; margin-bottom: 5px;">${name}</div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Original:</span>
                        <span style="color: ${oVuln ? 'var(--color-weak)' : 'var(--color-very-strong)'}">${oVuln ? '❌ Vulnerable' : '✅ Safe'}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Improved:</span>
                        <span style="color: ${iVuln ? 'var(--color-weak)' : 'var(--color-very-strong)'}">${iVuln ? '❌ Vulnerable' : '✅ Safe'}</span>
                    </div>
                </div>
                `;
            }
            document.getElementById('comp-attack-grid').innerHTML = gridHtml;
        }

"""

# Hook up btn-improve visibility to analyzing
# Replace `function updateUI(data) { ... }` with version that shows button
update_ui = """function updateUI(data) {"""
update_ui_replacement = """function updateUI(data) {
            btnImprove.style.display = 'block';
            compSection.classList.remove('show');"""
content = content.replace(update_ui, update_ui_replacement)

# Update resetUI to hide the button
reset_ui = """function resetUI() {"""
reset_ui_replacement = """function resetUI() {
            btnImprove.style.display = 'none';
            compSection.classList.remove('show');"""
content = content.replace(reset_ui, reset_ui_replacement)

# Insert the script JS addition right before closing </script>
content = content.replace("</script>\n</body>", js_addition + "\n    </script>\n</body>")

with open("d:/passwordproject/patch_html.py", "w", encoding="utf-8") as f:
    f.write(f'''# Patch index.html
with open("d:/passwordproject/index.html", "w", encoding="utf-8") as f:
    f.write("""{content}""")
''')
