from flask import Flask, render_template, request, jsonify
from similarity import check_novelty
from ai_suggestions import generate_suggestions
import random

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
    # Calculate 5 radar dimensions based on novelty score
    similarity = avg_similarity or (100 - novelty_score)
    
    originality = round(novelty_score * 0.95 + random.uniform(-3, 3), 1)
    market_gap = round(novelty_score * 0.85 + random.uniform(-5, 5), 1)
    competition = round((100 - similarity) * 0.90 + random.uniform(-3, 3), 1)
    innovation = round(novelty_score * 0.80 + random.uniform(-8, 8), 1)
    viability = round(50 + (novelty_score - 50) * 0.4 + random.uniform(-5, 5), 1)

    # Clamp all values between 5 and 98
    def clamp(v): return max(5, min(98, v))

    return {
        "originality": clamp(originality),
        "market_gap": clamp(market_gap),
        "competition": clamp(competition),
        "innovation": clamp(innovation),
        "viability": clamp(viability)
    }

def detect_category(idea):
    idea_lower = idea.lower()
    categories = {
        "Fintech": ["payment", "finance", "bank", "money", "invest", "crypto", "wallet", "loan", "insurance"],
        "Edtech": ["education", "learning", "course", "student", "school", "teach", "tutor", "skill"],
        "Healthtech": ["health", "medical", "doctor", "hospital", "medicine", "fitness", "wellness", "patient"],
        "Agritech": ["farm", "crop", "agriculture", "farmer", "soil", "irrigation", "harvest"],
        "Ecommerce": ["shop", "store", "buy", "sell", "product", "delivery", "marketplace", "retail"],
        "Foodtech": ["food", "restaurant", "meal", "recipe", "cook", "eat", "delivery", "chef"],
        "Transport": ["ride", "drive", "vehicle", "transport", "commute", "bike", "car", "taxi"],
        "AI/ML": ["ai", "artificial intelligence", "machine learning", "model", "data", "predict", "automate"],
        "SaaS": ["software", "platform", "tool", "dashboard", "api", "cloud", "saas", "automation"],
        "Social": ["social", "community", "connect", "network", "chat", "messaging", "friend"],
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
    data = request.get_json()
    user_idea = data.get("idea", "").strip()

    if not user_idea:
        return jsonify({"error": "Please enter a business idea"}), 400
    if len(user_idea) < 10:
        return jsonify({"error": "Please describe your idea in more detail"}), 400

    # Step 1: Similarity
    result = check_novelty(user_idea)
    novelty_score = result["novelty_score"]
    matches = result["matches"]
    avg_similarity = result.get("avg_similarity", 0)
    verdict = get_verdict(novelty_score)

    # Step 2: Radar scores
    radar = get_radar_scores(novelty_score, avg_similarity)

    # Step 3: Category
    category = detect_category(user_idea)

    # Step 4: AI suggestions
    print("🤖 Getting AI suggestions from Groq...")
    suggestions = generate_suggestions(user_idea, novelty_score, matches)

    return jsonify({
        "novelty_score": novelty_score,
        "verdict": verdict,
        "matches": matches,
        "suggestions": suggestions,
        "avg_similarity": avg_similarity,
        "radar": radar,
        "category": category
    })

if __name__ == "__main__":
    app.run(debug=True)