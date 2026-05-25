from flask import Flask, render_template, request, jsonify, send_file
from similarity import check_novelty
from ai_suggestions import generate_suggestions
from pdf_report import generate_dark_pdf
import random
import traceback
import io

app = Flask(__name__)

def get_verdict(novelty_score):
    if novelty_score >= 75:
        return {"label": "Highly Novel", "color": "green", "icon": "🟢"}
    elif novelty_score >= 50:
        return {"label": "Moderately Novel", "color": "gold", "icon": "🟡"}
    elif novelty_score >= 30:
        return {"label": "Somewhat Common", "color": "orange", "icon": "🟠"}
    else:
        return {"label": "Highly Similar", "color": "red", "icon": "🔴"}

def get_radar_scores(novelty_score, avg_similarity):
    similarity  = avg_similarity or (100 - novelty_score)
    originality = round(novelty_score * 0.95 + random.uniform(-3, 3), 1)
    market_gap  = round(novelty_score * 0.85 + random.uniform(-5, 5), 1)
    competition = round((100 - similarity) * 0.90 + random.uniform(-3, 3), 1)
    innovation  = round(novelty_score * 0.80 + random.uniform(-8, 8), 1)
    viability   = round(50 + (novelty_score - 50) * 0.4 + random.uniform(-5, 5), 1)
    def clamp(v): return max(5, min(98, v))
    return {
        "Originality": clamp(originality),
        "Market Gap":  clamp(market_gap),
        "Competition": clamp(competition),
        "Innovation":  clamp(innovation),
        "Viability":   clamp(viability),
    }

def detect_category(idea):
    idea_lower = idea.lower()
    categories = {
        "Fintech":    ["payment", "finance", "bank", "money", "invest", "crypto", "wallet", "loan", "insurance"],
        "Edtech":     ["education", "learning", "course", "student", "school", "teach", "tutor", "skill"],
        "Healthtech": ["health", "medical", "doctor", "hospital", "medicine", "fitness", "wellness", "patient"],
        "Agritech":   ["farm", "crop", "agriculture", "farmer", "soil", "irrigation", "harvest"],
        "Ecommerce":  ["shop", "store", "buy", "sell", "product", "delivery", "marketplace", "retail"],
        "Foodtech":   ["food", "restaurant", "meal", "recipe", "cook", "eat", "delivery", "chef"],
        "Transport":  ["ride", "drive", "vehicle", "transport", "commute", "bike", "car", "taxi"],
        "AI/ML":      ["ai", "artificial intelligence", "machine learning", "model", "data", "predict", "automate"],
        "SaaS":       ["software", "platform", "tool", "dashboard", "api", "cloud", "saas", "automation"],
        "Social":     ["social", "community", "connect", "network", "chat", "messaging", "friend"],
        "Design":     ["design", "agency", "branding", "creative", "web design", "graphic", "ui", "ux"],
    }
    for category, keywords in categories.items():
        if any(kw in idea_lower for kw in keywords):
            return category
    return "Technology"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data      = request.get_json(silent=True) or {}
    user_idea = (data.get("idea") or "").strip()

    if not user_idea:
        return jsonify({"error": "Please enter a business idea"}), 400
    if len(user_idea) < 10:
        return jsonify({"error": "Please describe your idea in more detail"}), 400

    try:
        print(f"\n{'='*60}")
        print(f"ANALYZING: {user_idea}")

        print("Step 1: Similarity check...")
        result         = check_novelty(user_idea)
        novelty_score  = result["novelty_score"]
        matches        = result["matches"]
        avg_similarity = result.get("avg_similarity", 0)
        verdict        = get_verdict(novelty_score)
        print(f"  Score: {novelty_score}% | Matches: {len(matches)}")

        print("Step 2: Radar scores...")
        radar = get_radar_scores(novelty_score, avg_similarity)

        category = detect_category(user_idea)
        print(f"  Category: {category}")

        print("Step 3: AI suggestions...")
        suggestions = generate_suggestions(user_idea, novelty_score, matches)
        print(f"  Got {len(suggestions)} suggestions")

        print("SUCCESS")
        return jsonify({
            "novelty_score":  novelty_score,
            "verdict":        verdict,
            "matches":        matches,
            "suggestions":    suggestions,
            "avg_similarity": avg_similarity,
            "radar":          radar,
            "category":       category,
        })

    except Exception as e:
        print("\n" + "!"*60)
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        print("!"*60)
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/download_report", methods=["POST"])
def download_report():
    """
    Generate and return a dark-theme PDF report.
    Expects the same JSON payload as /analyze results:
    {
        "idea": "...",
        "novelty_score": 50,
        "verdict": {"label": "Somewhat Common", ...},
        "category": "AI/ML",
        "radar": {"Originality": 46, ...},
        "matches": [...],
        "suggestions": [...],
        "avg_similarity": 45.2
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        idea           = (data.get("idea") or "Unknown Idea").strip()
        novelty_score  = float(data.get("novelty_score", 50))
        verdict_obj    = data.get("verdict", {})
        verdict_label  = verdict_obj.get("label", "Unknown") if isinstance(verdict_obj, dict) else str(verdict_obj)
        category       = data.get("category", "Technology")
        radar          = data.get("radar", {})
        matches        = data.get("matches", [])
        suggestions    = data.get("suggestions", [])
        avg_similarity = float(data.get("avg_similarity", 0))

        # Add rank to matches if missing
        for i, m in enumerate(matches):
            if "rank" not in m:
                m["rank"] = i + 1

        # Generate PDF bytes
        pdf_bytes = generate_dark_pdf(
            idea           = idea,
            novelty_score  = novelty_score,
            verdict        = verdict_label,
            category       = category,
            radar          = radar,
            matches        = matches,
            suggestions    = suggestions,
            avg_similarity = avg_similarity,
        )

        # Safe filename
        safe_name = "".join(c for c in idea[:30] if c.isalnum() or c in " _-").strip()
        safe_name = safe_name.replace(" ", "_") or "novelty_report"
        filename  = f"Business_Idea_Novelty_{safe_name}.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        print(f"PDF generation error: {e}")
        traceback.print_exc()
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)