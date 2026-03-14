let radarChartInstance = null;

async function analyzeIdea() {
    const idea = document.getElementById("ideaInput").value.trim();
    const btn = document.getElementById("analyzeBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    if (!idea) { alert("Please enter a business idea!"); return; }
    if (idea.length < 10) { alert("Please describe your idea in more detail!"); return; }

    btn.disabled = true;
    btnText.style.display = "none";
    btnLoader.style.display = "inline";
    document.getElementById("resultsSection").style.display = "none";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ idea: idea })
        });

        const data = await response.json();
        if (data.error) { alert(data.error); return; }
        displayResults(data);

    } catch (error) {
        alert("Something went wrong!");
        console.error(error);
    } finally {
        btn.disabled = false;
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
    }
}


function displayResults(data) {
    const { novelty_score, verdict, matches, suggestions, radar, category } = data;

    // ── SCORE ──
    document.getElementById("scoreBig").textContent = Math.round(novelty_score);
    document.getElementById("scoreLabel").textContent = verdict.label;
    document.getElementById("scoreIcon").textContent = verdict.icon;
    document.getElementById("scorePercent").textContent = Math.round(novelty_score) + "%";
    document.getElementById("categoryBadge").textContent = "◆ " + (category || "Technology");

    const colorMap = {
        green:  "#2ecc71",
        gold:   "#2ecc71",
        orange: "#f39c12",
        red:    "#e74c3c"
    };

    const scoreColor = colorMap[verdict.color] || "#2ecc71";
    document.getElementById("scoreBig").style.color = scoreColor;
    document.getElementById("scoreLabel").style.color = scoreColor;
    document.getElementById("scoreMeter").style.background =
        `linear-gradient(90deg, ${scoreColor}99, ${scoreColor})`;

    setTimeout(() => {
        document.getElementById("scoreMeter").style.width = novelty_score + "%";
    }, 100);

    // ── MATCHES ──
    const matchesList = document.getElementById("matchesList");
    matchesList.innerHTML = "";

    if (!matches || matches.length === 0) {
        matchesList.innerHTML = `
            <div class="match-card">
                <p style="font-style:italic; color:var(--muted); padding:20px 0; text-align:center;">
                    ✨ No similar companies found — your idea appears to be highly novel!
                </p>
            </div>`;
    } else {
        matches.forEach((match, index) => {
            const card = document.createElement("div");
            card.className = "match-card";
            card.style.opacity = "0";
            card.style.transform = "translateY(20px)";
            card.innerHTML = `
                <div class="match-top">
                    <div class="match-rank">MATCH #${index + 1}</div>
                    <div class="match-percent">${match.similarity}%</div>
                </div>
                <div class="match-name">${match.name}</div>
                <div class="match-desc">${match.description}</div>
                <div class="match-bar-bg">
                    <div class="match-bar-fill" id="bar${index}" style="width:0%"></div>
                </div>
            `;
            matchesList.appendChild(card);

            setTimeout(() => {
                card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
                card.style.opacity = "1";
                card.style.transform = "translateY(0)";
            }, index * 120);

            setTimeout(() => {
                const bar = document.getElementById(`bar${index}`);
                if (bar) bar.style.width = match.similarity + "%";
            }, 400 + index * 150);
        });
    }

    // ── RADAR CHART ──
    if (radar) {
        drawRadar(radar);
    }

    // ── SUGGESTIONS ──
    const suggestionsList = document.getElementById("suggestionsList");
    suggestionsList.innerHTML = "";

    if (!suggestions || suggestions.length === 0) {
        suggestionsList.innerHTML = `
            <div class="suggestion-card">
                <div class="suggestion-text">No suggestions available at this time.</div>
            </div>`;
    } else {
        suggestions.forEach((suggestion, index) => {
            const card = document.createElement("div");
            card.className = "suggestion-card";
            card.style.opacity = "0";
            card.style.transform = "translateX(20px)";
            card.innerHTML = `
                <div class="suggestion-num">0${index + 1}</div>
                <div class="suggestion-text">${suggestion}</div>
            `;
            suggestionsList.appendChild(card);

            setTimeout(() => {
                card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
                card.style.opacity = "1";
                card.style.transform = "translateX(0)";
            }, index * 100);
        });
    }

    // ── SHOW RESULTS ──
    document.getElementById("resultsSection").style.display = "block";
    setTimeout(() => {
        document.getElementById("resultsSection").scrollIntoView({
            behavior: "smooth", block: "start"
        });
    }, 100);
}


function drawRadar(radar) {
    const ctx = document.getElementById("radarChart").getContext("2d");

    if (radarChartInstance) {
        radarChartInstance.destroy();
        radarChartInstance = null;
    }

    const labels = ["Originality", "Market Gap", "Competition", "Innovation", "Viability"];
    const userScores = [
        radar.originality,
        radar.market_gap,
        radar.competition,
        radar.innovation,
        radar.viability
    ];

    // Market average baseline
    const marketAvg = userScores.map(s => Math.max(5, Math.min(60, 100 - s + 20)));

    radarChartInstance = new Chart(ctx, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Your Idea",
                    data: userScores,
                    backgroundColor: "rgba(46, 204, 113, 0.15)",
                    borderColor: "rgba(46, 204, 113, 0.9)",
                    borderWidth: 2,
                    pointBackgroundColor: "rgba(46, 204, 113, 1)",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: "Market Average",
                    data: marketAvg,
                    backgroundColor: "rgba(255, 255, 255, 0.03)",
                    borderColor: "rgba(255, 255, 255, 0.2)",
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    pointBackgroundColor: "rgba(255,255,255,0.4)",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1,
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1200,
                easing: "easeInOutQuart"
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 25,
                        display: false
                    },
                    grid: {
                        color: "rgba(255,255,255,0.06)",
                        lineWidth: 1
                    },
                    angleLines: {
                        color: "rgba(255,255,255,0.06)",
                        lineWidth: 1
                    },
                    pointLabels: {
                        color: "rgba(255,255,255,0.6)",
                        font: {
                            family: "Inter",
                            size: 11,
                            weight: "600"
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(0,0,0,0.8)",
                    borderColor: "rgba(46,204,113,0.3)",
                    borderWidth: 1,
                    titleColor: "#2ecc71",
                    bodyColor: "rgba(255,255,255,0.7)",
                    padding: 12,
                    callbacks: {
                        label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%`
                    }
                }
            }
        }
    });
}


document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("ideaInput").addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") analyzeIdea();
    });
});