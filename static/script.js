let radarChartInstance = null;
let currentData = null;
let allMatches = [];
let rotationTimer = null;

// ── 1. Core Analysis Logic (Diagnostic Mode) ────────────────────────
async function analyzeIdea() {
    const idea = document.getElementById("ideaInput").value.trim();
    const btn = document.getElementById("analyzeBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");
    const resultsSec = document.getElementById("resultsSection");

    if (!idea || idea.length < 10) { alert("Please describe your idea in more detail!"); return; }

    btn.disabled = true;
    btnText.style.display = "none";
    btnLoader.style.display = "inline";
    if (resultsSec) resultsSec.style.display = "none";

    try {
        const response = await fetch("/analyze", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idea })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        currentData = data;
        displayResults(data);
    } catch (error) {
        console.error("ANALYSIS ERROR:", error);
        alert("An error occurred: " + error.message);
    } finally {
        btn.disabled = false;
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
    }
}

// ── 2. Display Results Engine (Crash-Proof) ─────────────────────────
function displayResults(data) {
    try {
        const aiText = data.ai_analysis || "No AI strategy provided.";
        let extractedScore = 50;
        const scoreMatch = aiText.match(/(\d{1,3})%/);
        if (scoreMatch) extractedScore = parseInt(scoreMatch[1]);

        let verdict = { label: "Average", color: "orange" };
        if (extractedScore >= 80) verdict = { label: "Highly Original", color: "green" };
        else if (extractedScore >= 60) verdict = { label: "Promising", color: "gold" };
        else if (extractedScore < 40) verdict = { label: "Saturated", color: "red" };

        if(document.getElementById("scoreBig")) document.getElementById("scoreBig").textContent = extractedScore;
        if(document.getElementById("scoreLabel")) document.getElementById("scoreLabel").textContent = verdict.label;
        if(document.getElementById("scorePercent")) document.getElementById("scorePercent").textContent = extractedScore + "%";

        let extractedDomain = "UNCATEGORIZED";
        const domainMatch = aiText.match(/Industry Domain:\s*\*?\*?\s*([^\n\*]+)/i);
        if (domainMatch) extractedDomain = domainMatch[1].trim();

        if(document.getElementById("categoryBadge")) document.getElementById("categoryBadge").textContent = "◆ DOMAIN: " + extractedDomain.toUpperCase();

        const colorMap = { green: "#2ecc71", gold: "#e3a008", orange: "#f97316", red: "#ef4444" };
        const emojiMap = { green: "🌟", gold: "💡", orange: "⚠️", red: "🚨" };

        if(document.getElementById("scoreBig")) document.getElementById("scoreBig").style.color = colorMap[verdict.color] || "#2ecc71";
        if(document.getElementById("scoreMeter")) {
            document.getElementById("scoreMeter").style.width = extractedScore + "%";
            document.getElementById("scoreMeter").style.background = colorMap[verdict.color] || "#2ecc71";
        }
        if(document.getElementById("scoreIcon")) document.getElementById("scoreIcon").textContent = emojiMap[verdict.color] || "💡";

        allMatches = [];
        const indiaHubs = [{ lat: 12.9716, lng: 77.5946, city: "Bangalore" }, { lat: 17.3850, lng: 78.4867, city: "Hyderabad" }, { lat: 19.0760, lng: 72.8777, city: "Mumbai" }, { lat: 28.7041, lng: 77.1025, city: "New Delhi" }];
        const globalHubs = [{ lat: 37.7749, lng: -122.4194, city: "San Francisco" }, { lat: 51.5074, lng: -0.1278, city: "London" }, { lat: 1.3521, lng: 103.8198, city: "Singapore" }, { lat: 52.5200, lng: 13.4050, city: "Berlin" }];

        const indiaList = (data.competitors && data.competitors.india) ? data.competitors.india : [];
        const globalList = (data.competitors && data.competitors.global) ? data.competitors.global : [];

        indiaList.forEach((c, i) => {
            const hub = indiaHubs[i % indiaHubs.length];
            allMatches.push({ name: c.name || "Unknown", url: c.url || "", description: c.desc || c.description || "No description.", country: "India", flag: "🇮🇳", similarity: c.similarity || Math.floor(Math.random() * 20 + 75), lat: hub.lat, lng: hub.lng, city: hub.city });
        });
        globalList.forEach((c, i) => {
            const hub = globalHubs[i % globalHubs.length];
            allMatches.push({ name: c.name || "Unknown", url: c.url || "", description: c.desc || c.description || "No description.", country: "Global", flag: "🌐", similarity: c.similarity || Math.floor(Math.random() * 20 + 60), lat: hub.lat, lng: hub.lng, city: hub.city });
        });

        filterByLocation('all');

        const radar = { Originality: extractedScore, "Market Gap": Math.min(100, extractedScore + 15), Competition: 100 - extractedScore, Innovation: Math.max(0, extractedScore - 5), Viability: 85 };
        drawRadar(radar);

        // ── MAGIC FIX: Beautiful AI Text Formatting & Highlighting ───────────────────
        let formattedAI = aiText
            .replace(/\*\*Industry Domain:\*\*.*\n?/i, '')
            .replace(/\*\*Novelty Score:\*\*.*\n?/i, '')
            .replace(/\n/g, '<br>')
            // Target the **Bold Headings** (Now keeping the numbers attached!)
            .replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--emerald); font-size: 13px; letter-spacing: 1px; display: block; margin-top: 22px; margin-bottom: 6px; text-transform: uppercase; border-bottom: 1px solid rgba(46,204,113,0.15); padding-bottom: 4px;">$1</strong>')
            // Target the ==Highlighted Sentences== and make them glow
            .replace(/==(.*?)==/g, '<span style="color: #ffffff; background: rgba(46, 204, 113, 0.2); padding: 3px 6px; border-radius: 4px; font-weight: 600; border: 1px solid rgba(46,204,113,0.3); box-shadow: 0 0 10px rgba(46,204,113,0.1);">$1</span>')
            // Clean up any double-spacing caused by the br replacements
            .replace(/(<br>\s*){2,}/g, '<br><br>');
        
        if(document.getElementById("suggestionsList")) {
            document.getElementById("suggestionsList").innerHTML = `
                <div class="suggestion-card">
                    <div class="suggestion-num" style="color: var(--emerald); font-size: 28px; line-height: 1.2;">✦</div>
                    <div class="suggestion-text" style="line-height: 1.8; padding-bottom: 15px;">${formattedAI}</div>
                </div>`;
        }

        document.getElementById("resultsSection").style.display = "block";
        document.getElementById("resultsSection").scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        console.error("UI Rendering Error:", err);
    }
}

// ── 3. Map Toggles & UI ─────────────────────────────────────────────
function filterByLocation(type) {
    document.querySelectorAll(".loc-btn").forEach(b => b.classList.remove("active-loc"));
    if(document.getElementById("btn-" + type)) document.getElementById("btn-" + type).classList.add("active-loc");
    const matchesList = document.getElementById("matchesList");
    const existingMap = document.getElementById("mapPanel");
    if (existingMap) existingMap.remove();
    if (rotationTimer) { rotationTimer.stop(); rotationTimer = null; }

    let filteredMatches = [];
    if (type === "india") { filteredMatches = allMatches.filter(m => m.country === "India"); renderIndiaView(filteredMatches, matchesList); } 
    else if (type === "global") { filteredMatches = allMatches.filter(m => m.country !== "India"); render3GlobeView(filteredMatches, matchesList); } 
    else { filteredMatches = allMatches; renderMatchCards(filteredMatches, matchesList); }
}

function renderIndiaView(matches, container) {
    if (typeof d3 === 'undefined') { renderMatchCards(matches, container); return; }
    const panel = document.createElement("div");
    panel.id = "mapPanel";
    panel.className = "glass-card";
    panel.innerHTML = `<div style="padding:20px; border-bottom:1px solid var(--border);"><span style="font-size:12px; font-weight:700; color:var(--emerald); letter-spacing: 2px;">INDIA COMPETITOR HEATMAP</span></div><div id="mapContainer" style="height:500px; position:relative; display:flex; justify-content:center; align-items:center; background:rgba(0,0,0,0.2);"><svg id="indiaMapSvg" viewBox="0 0 800 800" style="width:100%; height:100%;"></svg></div>`;
    container.parentNode.insertBefore(panel, container);
    const svg = d3.select("#indiaMapSvg");
    const projection = d3.geoMercator().scale(1200).center([82.8, 23.5]).translate([400, 400]);
    const path = d3.geoPath().projection(projection);

    fetch("https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States").then(res => res.json()).then(geojson => {
        svg.selectAll("path").data(geojson.features).enter().append("path").attr("d", path).attr("class", "state-path").attr("fill", "rgba(255,255,255,0.05)").attr("stroke", "rgba(255,255,255,0.1)");
        svg.selectAll("circle.dot").data(matches).enter().append("circle").attr("class", "dot").attr("cx", d => projection([d.lng, d.lat])[0]).attr("cy", d => projection([d.lng, d.lat])[1]).attr("r", 8).attr("fill", "#2ecc71").attr("stroke", "#111").attr("stroke-width", 2).style("filter", "drop-shadow(0px 0px 6px rgba(46,204,113,0.8))");
    }).catch(e => console.warn("Map failed:", e));
    renderMatchCards(matches, container);
}

function render3GlobeView(matches, container) {
    if (typeof d3 === 'undefined') { renderMatchCards(matches, container); return; }
    const panel = document.createElement("div");
    panel.id = "mapPanel";
    panel.className = "glass-card";
    panel.innerHTML = `<div style="padding:20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;"><span style="font-size:12px; font-weight:700; color:var(--emerald); letter-spacing: 2px;">GLOBAL 3D COMPETITOR HEATMAP</span></div><div id="mapContainer" style="height:450px; position:relative; background:radial-gradient(circle at center, rgba(30,40,40,1) 0%, rgba(10,10,10,1) 100%); cursor: grab; display:flex; justify-content:center; align-items:center;"><svg id="worldMapSvg" viewBox="0 0 800 450" style="width:100%; height:100%;"></svg></div>`;
    container.parentNode.insertBefore(panel, container);
    const svg = d3.select("#worldMapSvg");
    const projection = d3.geoOrthographic().scale(200).translate([400, 225]).clipAngle(90);
    const path = d3.geoPath().projection(projection);

    svg.append("circle").attr("cx", 400).attr("cy", 225).attr("r", 200).attr("fill", "rgba(0,0,0,0.4)").attr("stroke", "rgba(46,204,113,0.2)");
    fetch("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").then(res => res.json()).then(world => {
        const mapGroup = svg.append("g");
        function render() {
            mapGroup.selectAll("*").remove();
            mapGroup.selectAll("path").data(world.features).enter().append("path").attr("d", path).attr("class", "country").attr("fill", "rgba(255,255,255,0.05)").attr("stroke", "rgba(255,255,255,0.1)");
            mapGroup.selectAll("circle.dot").data(matches).enter().append("circle").attr("class", "dot").attr("cx", d => projection([d.lng, d.lat]) ? projection([d.lng, d.lat])[0] : 0).attr("cy", d => projection([d.lng, d.lat]) ? projection([d.lng, d.lat])[1] : 0).attr("r", 6).attr("fill", "#2ecc71").style("display", d => d3.geoDistance([d.lng, d.lat], projection.invert([400, 225])) > Math.PI / 2 ? "none" : "block").style("filter", "drop-shadow(0px 0px 4px rgba(46,204,113,0.8))");
        }
        rotationTimer = d3.timer(() => { projection.rotate([projection.rotate()[0] + 0.2, -15]); render(); });
        const drag = d3.drag().on("start", () => { if (rotationTimer) { rotationTimer.stop(); rotationTimer = null; } }).on("drag", (e) => { projection.rotate([projection.rotate()[0] + e.dx * 0.5, projection.rotate()[1] - e.dy * 0.5]); render(); });
        svg.call(drag); render();
    }).catch(e => console.warn("Globe failed:", e));
    renderMatchCards(matches, container);
}

function renderMatchCards(matches, container) {
    if (!matches || matches.length === 0) { container.innerHTML = `<div style="text-align:center; padding:40px; color:var(--muted); border: 1px dashed var(--border); border-radius:12px;">No competitors found.</div>`; return; }
    container.innerHTML = matches.map((m, i) => {
        let shortDesc = (m.description || '').substring(0, 150) + '...';
        let cleanName = (m.name || 'Unknown Company').split('|')[0].split(' - ')[0].trim();
        let cleanUrl = ""; if (m.url) { try { cleanUrl = new URL(m.url).hostname.replace('www.', ''); } catch (e) { } }
        return `
        <div class="match-card">
            <div class="match-top"><div class="match-rank">MATCH #${i + 1} — ${m.flag || '🌐'} ${m.city || m.country}</div><div class="match-percent">${Math.round(m.similarity || 0)}%</div></div>
            <div class="match-name">${m.url ? `<a href="${m.url}" target="_blank" style="color:var(--emerald); text-decoration:none;" onmouseover="this.style.color='var(--white)'" onmouseout="this.style.color='var(--emerald)'">${cleanName} <span style="font-size:12px;">↗</span></a>` : cleanName}
            ${cleanUrl ? `<div style="font-size: 11px; opacity: 0.8; margin-top: 3px; font-family: monospace; letter-spacing: 0.5px;">${cleanUrl}</div>` : ''}</div>
            <div class="match-desc">${shortDesc}</div>
            <div class="match-bar-bg"><div class="match-bar-fill" style="width:${m.similarity || 0}%"></div></div>
        </div>`
    }).join("");
}

function drawRadar(radar) {
    if (typeof Chart === 'undefined') return;
    if (radarChartInstance) radarChartInstance.destroy();
    Chart.defaults.color = 'rgba(255, 255, 255, 0.5)'; Chart.defaults.font.family = 'Inter';
    try {
        radarChartInstance = new Chart(document.getElementById("radarChart").getContext("2d"), {
            type: 'radar',
            data: { labels: ["Originality", "Market Gap", "Competition", "Innovation", "Viability"], datasets: [{ label: 'Analysis Score', data: [radar.Originality, radar["Market Gap"], radar.Competition, radar.Innovation, radar.Viability], borderColor: '#2ecc71', backgroundColor: 'rgba(46, 204, 113, 0.2)', borderWidth: 2, pointBackgroundColor: '#2ecc71', pointRadius: 3 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { r: { angleLines: { color: 'rgba(255, 255, 255, 0.1)' }, grid: { color: 'rgba(255, 255, 255, 0.1)' }, pointLabels: { color: 'rgba(255, 255, 255, 0.7)', font: { size: 11 } }, ticks: { display: false, maxTicksLimit: 5 }, min: 0, max: 100 } } }
        });
    } catch(e) { console.warn("Chart failed", e); }
}

// ── 8. PDF Download Utility (Native A4 Document Builder) ──────────
async function downloadPDF() {
    const btn = document.getElementById("downloadBtn");
    btn.textContent = "⏳ GENERATING REPORT...";
    btn.disabled = true;

    try {
        const radarCanvas = document.getElementById("radarChart");
        const radarImg = radarCanvas ? radarCanvas.toDataURL("image/png", 1.0) : "";

        const score = document.getElementById("scoreBig").innerText || "--";
        const verdict = document.getElementById("scoreLabel").innerText || "--";
        const domain = document.getElementById("categoryBadge").innerText || "DOMAIN: UNCATEGORIZED";
        const aiStrategy = document.getElementById("suggestionsList").innerHTML || "";

        const buildCards = (matches) => {
            if (!matches || matches.length === 0) return '<div style="color:#777; padding:20px; text-align:center;">No matches found.</div>';
            return matches.map((m, i) => `
                <div style="background: #222; border-left: 4px solid #2ecc71; padding: 15px; margin-bottom: 15px; border-radius: 4px; page-break-inside: avoid;">
                    <div style="font-size: 10px; color: #aaa; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px; text-transform: uppercase;">MATCH #${i + 1} &nbsp;|&nbsp; ${m.flag || ''} ${m.city || m.country} &nbsp;|&nbsp; <span style="color:#2ecc71">${Math.round(m.similarity)}% SIMILAR</span></div>
                    <div style="font-size: 16px; color: #fff; font-weight: bold; margin-bottom: 5px;">${m.name}</div>
                    <div style="font-size: 12px; color: #ddd; line-height: 1.5;">${(m.description || '').substring(0, 180)}...</div>
                </div>
            `).join('');
        };

        const indiaHTML = buildCards(allMatches.filter(m => m.country === "India").slice(0, 5));
        const globalHTML = buildCards(allMatches.filter(m => m.country !== "India").slice(0, 5));

        const printWindow = window.open('', '_blank');
        const html = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Business Idea Novelty Report</title>
            <style>
                @page { size: A4 portrait; margin: 15mm; }
                body { font-family: 'Inter', Arial, sans-serif; background-color: #1a1a1a; color: #ffffff; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; margin: 0; }
                .header { text-align: center; border-bottom: 1px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
                .header h1 { color: #ffffff; margin: 0; font-size: 32px; font-weight: 900; }
                .header h1 span { color: #2ecc71; font-style: italic; }
                .header p { color: #888; font-size: 12px; letter-spacing: 4px; margin-top: 5px; }
                .flex-container { display: flex; gap: 30px; margin-bottom: 30px; }
                .score-box { flex: 1; background: #222; border: 1px solid #333; border-radius: 12px; padding: 30px; text-align: center; }
                .score-box .num { font-size: 70px; font-weight: 900; color: #2ecc71; margin: 0; line-height: 1; }
                .score-box .label { font-size: 20px; color: #fff; margin: 10px 0; font-style: italic; }
                .score-box .domain { display: inline-block; background: rgba(46, 204, 113, 0.1); border: 1px solid #2ecc71; color: #2ecc71; font-size: 10px; padding: 5px 15px; border-radius: 20px; letter-spacing: 1px; font-weight: bold; }
                .chart-box { flex: 1; background: #222; border: 1px solid #333; border-radius: 12px; padding: 20px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
                .chart-box img { max-width: 100%; max-height: 220px; }
                .section-title { font-size: 16px; color: #fff; border-bottom: 2px solid #2ecc71; padding-bottom: 8px; margin: 30px 0 20px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; display: inline-block;}
                .ai-box { background: #222; border: 1px solid #333; border-radius: 12px; padding: 25px; font-size: 13px; line-height: 1.8; color: #ccc; }
                
                /* Maintain the exact same highlighted style for the PDF! */
                .ai-box strong { color: #2ecc71 !important; font-size: 13px; letter-spacing: 1px; display: block; margin-top: 22px; margin-bottom: 6px; text-transform: uppercase; border-bottom: 1px solid rgba(46,204,113,0.15); padding-bottom: 4px; }
                .ai-box span { color: #ffffff !important; background: rgba(46, 204, 113, 0.2) !important; padding: 3px 6px; border-radius: 4px; font-weight: 600; border: 1px solid rgba(46,204,113,0.3); box-shadow: 0 0 10px rgba(46,204,113,0.1); }
                
                .ai-box .suggestion-num { display: none; }
                .ai-box .suggestion-card { background: none; border: none; padding: 0; margin: 0; }
                .grid-container { display: flex; gap: 30px; }
                .grid-col { flex: 1; }
            </style>
        </head>
        <body>
            <div class="header"><h1>Business Idea <span>Novelty</span></h1><p>INTELLIGENCE REPORT</p></div>
            <div class="flex-container"><div class="score-box"><p style="margin:0 0 15px 0; color:#888; font-size:11px; font-weight:bold; letter-spacing:2px;">NOVELTY VERDICT</p><p class="num">${score}</p><p class="label">${verdict}</p><div class="domain">${domain}</div></div><div class="chart-box"><p style="margin:0 0 15px 0; color:#888; font-size:11px; font-weight:bold; letter-spacing:2px;">INNOVATION RADAR</p><img src="${radarImg}" /></div></div>
            <div class="section-title">Strategic AI Recommendations</div>
            <div class="ai-box">${aiStrategy}</div>
            <div style="page-break-before: always;"></div>
            <div class="grid-container"><div class="grid-col"><div class="section-title">Indian Markets</div>${indiaHTML}</div><div class="grid-col"><div class="section-title">Global Markets</div>${globalHTML}</div></div>
        </body>
        </html>
        `;

        printWindow.document.open();
        printWindow.document.write(html);
        printWindow.document.close();

        setTimeout(() => {
            printWindow.focus();
            printWindow.print();
            btn.textContent = "📄 DOWNLOAD FULL REPORT";
            btn.disabled = false;
        }, 800);

    } catch (error) {
        console.error("PDF Generation Error:", error);
        alert("There was an error generating the PDF.");
        btn.textContent = "📄 DOWNLOAD FULL REPORT";
        btn.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("ideaInput");
    if (input) input.addEventListener("keydown", e => { if (e.ctrlKey && e.key === "Enter") analyzeIdea(); });
});