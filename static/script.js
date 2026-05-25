let radarChartInstance = null;
let currentData = null;
let allMatches = [];
let rotationTimer = null;

// ── 1. Core Analysis Logic ──────────────────────────────────────────
async function analyzeIdea() {
    const idea = document.getElementById("ideaInput").value.trim();
    const btn = document.getElementById("analyzeBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    if (!idea || idea.length < 10) { alert("Please describe your idea in more detail!"); return; }

    btn.disabled = true;
    btnText.style.display = "none";
    btnLoader.style.display = "inline";
    document.getElementById("resultsSection").style.display = "none";

    try {
        const response = await fetch("/analyze", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idea })
        });
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        currentData = data;
        currentData.idea = idea;
        displayResults(data);
    } catch (error) {
        console.error(error);
        alert("Analysis failed. Please check the console.");
    } finally {
        btn.disabled = false;
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
    }
}

// ── 2. Display Results ──────────────────────────────────────────────
function displayResults(data) {
    const { novelty_score, verdict, matches, suggestions, radar, category } = data;

    // Update Banner Score and Text
    document.getElementById("scoreBig").textContent = Math.round(novelty_score);
    document.getElementById("scoreLabel").textContent = verdict.label;
    document.getElementById("scorePercent").textContent = Math.round(novelty_score) + "%";
    document.getElementById("categoryBadge").textContent = "◆ " + (category || "Technology");

    // Dynamic Colors based on Score
    const colorMap = { green: "#2ecc71", gold: "#e3a008", orange: "#f97316", red: "#ef4444" };
    const emojiMap = { green: "🌟", gold: "💡", orange: "⚠️", red: "🚨" };

    document.getElementById("scoreBig").style.color = colorMap[verdict.color] || "#2ecc71";
    document.getElementById("scoreMeter").style.width = novelty_score + "%";
    document.getElementById("scoreMeter").style.background = colorMap[verdict.color] || "#2ecc71";
    document.getElementById("scoreIcon").textContent = emojiMap[verdict.color] || "💡";

    allMatches = matches || [];

    // Default to 'All' view and draw radar
    filterByLocation('all');
    if (radar) drawRadar(radar);

    // Update AI Recommendations
    const suggestionsList = document.getElementById("suggestionsList");
    suggestionsList.innerHTML = suggestions.map((s, i) => `
        <div class="suggestion-card">
            <div class="suggestion-num">0${i + 1}</div>
            <div class="suggestion-text">${s}</div>
        </div>`).join("");

    document.getElementById("resultsSection").style.display = "block";
    document.getElementById("resultsSection").scrollIntoView({ behavior: "smooth" });
}

// ── 3. Smart Map Toggles ────────────────────────────────────────────
function filterByLocation(type) {
    document.querySelectorAll(".loc-btn").forEach(b => b.classList.remove("active-loc"));
    document.getElementById("btn-" + type).classList.add("active-loc");

    const matchesList = document.getElementById("matchesList");
    const existingMap = document.getElementById("mapPanel");

    // Clear out any existing map (India or Globe)
    if (existingMap) existingMap.remove();

    // Stop the globe from spinning in the background to save memory
    if (rotationTimer) { rotationTimer.stop(); rotationTimer = null; }

    let filteredMatches = [];
    if (type === "india") {
        filteredMatches = allMatches.filter(m => m.country === "India" || m.flag === "🇮🇳");
        renderIndiaView(filteredMatches, matchesList);
    } else if (type === "global") {
        filteredMatches = allMatches.filter(m => m.country !== "India" && m.flag !== "🇮🇳");
        render3DGlobeView(filteredMatches, matchesList);
    } else {
        // "ALL" TOGGLE: Skip the globe and only render the competitor cards
        filteredMatches = allMatches;
        renderMatchCards(filteredMatches, matchesList);
    }
}

// ── 4. India Interactive Map (D3.js) ────────────────────────────────
function renderIndiaView(matches, container) {
    const panel = document.createElement("div");
    panel.id = "mapPanel";
    panel.className = "glass-card";
    panel.innerHTML = `<div style="padding:20px; border-bottom:1px solid var(--border);"><span style="font-size:12px; font-weight:700; color:var(--emerald); letter-spacing: 2px;">INDIA COMPETITOR HEATMAP</span></div><div id="mapContainer" style="height:500px; position:relative; display:flex; justify-content:center; align-items:center; background:rgba(0,0,0,0.2);"><svg id="indiaMapSvg" viewBox="0 0 800 800" style="width:100%; height:100%;"></svg><div id="mapTooltip" style="position:absolute; background:rgba(10,10,10,0.95); border:1px solid var(--emerald); padding:12px; border-radius:8px; opacity:0; pointer-events:none; z-index:100; color:#fff; font-size:12px;"></div></div>`;
    container.parentNode.insertBefore(panel, container);

    const svg = d3.select("#indiaMapSvg");
    const projection = d3.geoMercator().scale(1200).center([82.8, 23.5]).translate([400, 400]);
    const path = d3.geoPath().projection(projection);

    fetch("https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States").then(res => res.json()).then(geojson => {
        svg.selectAll("path").data(geojson.features).enter().append("path").attr("d", path).attr("class", "state-path");

        svg.selectAll("circle").data(matches.filter(m => m.lat && m.lng)).enter().append("circle")
            .attr("cx", d => projection([d.lng, d.lat])[0]).attr("cy", d => projection([d.lng, d.lat])[1])
            .attr("r", d => 5 + (d.similarity / 15))
            .attr("fill", "var(--emerald)")
            .style("filter", "drop-shadow(0 0 8px var(--emerald))")
            .on("mouseenter", function (e, d) {
                d3.select(this).attr("r", 10);
                const tip = document.getElementById("mapTooltip");
                tip.style.opacity = "1";
                tip.innerHTML = `<strong style="color:var(--emerald); text-transform:uppercase;">${d.name}</strong><br><div style="margin-top:6px; color:var(--muted);">${d.sector || 'Tech'} • ${d.city || 'India'}</div><div style="margin-top:4px; font-weight:bold;">Similarity: ${Math.round(d.similarity)}%</div>`;
            })
            .on("mousemove", e => {
                const tip = document.getElementById("mapTooltip");
                const rect = document.getElementById("mapContainer").getBoundingClientRect();
                tip.style.left = (e.clientX - rect.left + 15) + "px";
                tip.style.top = (e.clientY - rect.top - 40) + "px";
            })
            .on("mouseleave", function (e, d) {
                d3.select(this).attr("r", 5 + (d.similarity / 15));
                document.getElementById("mapTooltip").style.opacity = "0";
            });
    });
    renderMatchCards(matches, container);
}

// ── 5. Global 3D Rotating Globe (D3.js) ─────────────────────────────
function render3DGlobeView(matches, container) {
    const panel = document.createElement("div");
    panel.id = "mapPanel";
    panel.className = "glass-card";
    panel.innerHTML = `<div style="padding:20px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;"><span style="font-size:12px; font-weight:700; color:var(--emerald); letter-spacing: 2px;">GLOBAL 3D COMPETITOR HEATMAP</span><span style="font-size:12px; color:var(--muted);">Drag to Rotate</span></div><div id="mapContainer" style="height:450px; position:relative; background:radial-gradient(circle at center, rgba(30,40,40,1) 0%, rgba(10,10,10,1) 100%); cursor: grab; display:flex; justify-content:center; align-items:center;"><svg id="worldMapSvg" viewBox="0 0 800 450" style="width:100%; height:100%;"></svg><div id="mapTooltip" style="position:absolute; background:rgba(10,10,10,0.95); border:1px solid var(--emerald); padding:12px; border-radius:8px; opacity:0; pointer-events:none; z-index:100; color:#fff; font-size:12px;"></div></div>`;
    container.parentNode.insertBefore(panel, container);

    const svg = d3.select("#worldMapSvg");
    const projection = d3.geoOrthographic().scale(200).translate([400, 225]).clipAngle(90);
    const path = d3.geoPath().projection(projection);

    // Ocean background
    svg.append("circle").attr("cx", 400).attr("cy", 225).attr("r", 200).attr("fill", "rgba(0,0,0,0.4)").attr("stroke", "rgba(46,204,113,0.2)");

    fetch("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").then(res => res.json()).then(world => {
        const mapGroup = svg.append("g");

        function render() {
            mapGroup.selectAll("*").remove();

            // Draw countries
            mapGroup.selectAll("path").data(world.features).enter().append("path").attr("d", path).attr("class", "country").attr("fill", "rgba(255,255,255,0.05)").attr("stroke", "rgba(255,255,255,0.1)");

            // Draw pins
            mapGroup.selectAll("circle").data(matches.filter(m => m.lat && m.lng)).enter().append("circle")
                .attr("cx", d => { const p = projection([d.lng, d.lat]); return p ? p[0] : -1000; })
                .attr("cy", d => { const p = projection([d.lng, d.lat]); return p ? p[1] : -1000; })
                .attr("r", d => {
                    const dist = d3.geoDistance(projection.invert([400, 225]), [d.lng, d.lat]);
                    return dist > Math.PI / 2 ? 0 : 5 + (d.similarity / 15);
                })
                .attr("fill", d => d.country === 'India' ? '#f97316' : '#2ecc71')
                .style("filter", d => d.country === 'India' ? "drop-shadow(0 0 6px #f97316)" : "drop-shadow(0 0 6px #2ecc71)")
                .on("mouseenter", function (e, d) {
                    const tip = document.getElementById("mapTooltip");
                    tip.style.opacity = "1";
                    tip.innerHTML = `<strong style="color:var(--emerald); text-transform:uppercase;">${d.name}</strong><br><div style="margin-top:6px; color:var(--muted);">${d.sector || 'Tech'} • ${d.city || d.country}</div><div style="margin-top:4px; font-weight:bold;">Similarity: ${Math.round(d.similarity)}%</div>`;
                })
                .on("mousemove", e => {
                    const tip = document.getElementById("mapTooltip");
                    const rect = document.getElementById("mapContainer").getBoundingClientRect();
                    tip.style.left = (e.clientX - rect.left + 15) + "px";
                    tip.style.top = (e.clientY - rect.top - 40) + "px";
                })
                .on("mouseleave", () => document.getElementById("mapTooltip").style.opacity = "0");
        }

        // Auto-rotation logic
        rotationTimer = d3.timer(() => {
            projection.rotate([projection.rotate()[0] + 0.2, -15]);
            render();
        });

        // Drag to rotate manually
        const drag = d3.drag().on("start", () => {
            if (rotationTimer) { rotationTimer.stop(); rotationTimer = null; }
        }).on("drag", (e) => {
            const rot = projection.rotate();
            projection.rotate([rot[0] + e.dx * 0.5, rot[1] - e.dy * 0.5]);
            render();
        });
        svg.call(drag);
        render();
    });
    renderMatchCards(matches, container);
}

// ── 6. Competitor Cards List ────────────────────────────────────────
function renderMatchCards(matches, container) {
    if (!matches || matches.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding:40px; color:var(--muted); border: 1px dashed var(--border); border-radius:12px;">No competitors found for this filter.</div>`;
        return;
    }
    container.innerHTML = matches.map((m, i) => `
        <div class="match-card">
            <div class="match-top">
                <div class="match-rank">MATCH #${i + 1} — ${m.flag || '🌐'} ${m.country || 'Global'}</div>
                <div class="match-percent">${Math.round(m.similarity || 0)}%</div>
            </div>
            <div class="match-name">
                ${m.url ? `<a href="${m.url}" target="_blank" style="color:var(--white); text-decoration:none;" onmouseover="this.style.color='var(--emerald)'" onmouseout="this.style.color='var(--white)'">${m.name} <span style="color:var(--emerald); font-size:12px;">↗</span></a>` : m.name}
            </div>
            <div class="match-desc">${m.description || ''}</div>
            <div class="match-bar-bg"><div class="match-bar-fill" style="width:${m.similarity || 0}%"></div></div>
        </div>`).join("");
}

// ── 7. Fully Styled Radar Chart (Chart.js) ──────────────────────────
function drawRadar(radar) {
    if (radarChartInstance) radarChartInstance.destroy();

    // Set global chart defaults for the dark theme
    Chart.defaults.color = 'rgba(255, 255, 255, 0.5)';
    Chart.defaults.font.family = 'Inter';

    radarChartInstance = new Chart(document.getElementById("radarChart").getContext("2d"), {
        type: 'radar',
        data: {
            labels: ["Originality", "Market Gap", "Competition", "Innovation", "Viability"],
            datasets: [{
                label: 'Analysis Score',
                data: [radar.Originality, radar["Market Gap"], radar.Competition, radar.Innovation, radar.Viability],
                borderColor: '#2ecc71',
                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                borderWidth: 2,
                pointBackgroundColor: '#2ecc71',
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false } // Hides the "Analysis Score" box at the top
            },
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: { size: 11 }
                    },
                    ticks: {
                        display: false, // Hides the white numbers in the center
                        maxTicksLimit: 5
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// ── 8. PDF Download Utility ─────────────────────────────────────────
async function downloadPDF() {
    if (!currentData) return;
    const btn = document.getElementById("downloadBtn");
    btn.textContent = "⏳ GENERATING PDF..."; btn.disabled = true;
    try {
        const response = await fetch("/download_report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(currentData) });
        if (!response.ok) throw new Error("Server failed");
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "MCA_Business_Idea_Report.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } catch (err) {
        console.error(err);
        alert("Failed to generate PDF.");
    } finally {
        btn.textContent = "📄 DOWNLOAD FULL REPORT"; btn.disabled = false;
    }
}

// ── 9. Keyboard Shortcuts ───────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("ideaInput");
    if (input) {
        input.addEventListener("keydown", e => {
            if (e.ctrlKey && e.key === "Enter") analyzeIdea();
        });
    }
});