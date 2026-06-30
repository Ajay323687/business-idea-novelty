import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from exa_py import Exa
from groq import Groq
from sentence_transformers import SentenceTransformer, util

# Load the secret keys from your .env file
load_dotenv()

app = Flask(__name__)

# Initialize our AI clients securely
exa = Exa(api_key=os.getenv("EXA_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Loading SBERT Semantic Engine (all-MiniLM-L6-v2)...")
sbert_model = SentenceTransformer('all-MiniLM-L6-v2') 
print("SBERT Engine Loaded Successfully!")

def run_dual_mission_analysis(business_idea):
    print(f"\n[Exa.ai] Fetching live competitors for: '{business_idea}'")
    
    # 1. RETRIEVAL LAYER (EXA AI NEURAL SEARCH)
    india_list = []
    try:
        india_results = exa.search(f"A top {business_idea} company or startup based in India", type="neural", category="company", num_results=5)
        india_list = [{"name": r.title, "url": r.url, "desc": str(getattr(r, 'text', 'No description provided.'))[:800]} for r in india_results.results] if india_results else []
    except Exception as e:
        print(f"[Exa.ai] India Mission failed: {e}")

    global_list = []
    try:
        global_results = exa.search(f"A successful {business_idea} company or startup", type="neural", category="company", num_results=10)
        india_urls = {comp["url"] for comp in india_list}
        
        if global_results:
            for r in global_results.results:
                if r.url not in india_urls and len(global_list) < 5:
                    global_list.append({"name": r.title, "url": r.url, "desc": str(getattr(r, 'text', 'No description provided.'))[:800]})
    except Exception as e:
        print(f"[Exa.ai] Global Mission failed: {e}")

    all_competitors = india_list + global_list
    if not all_competitors:
        return {"error": "No competitors found to analyze. Try being more descriptive."}

    # 2. SEMANTIC ENCODING & COSINE SIMILARITY LAYER (SBERT)
    print("[SBERT] Calculating Spatial Vectors and Cosine Similarity...")
    idea_embedding = sbert_model.encode(business_idea, convert_to_tensor=True)
    max_similarity = 0.0

    for comp in all_competitors:
        comp_embedding = sbert_model.encode(comp["desc"], convert_to_tensor=True)
        sim_score = util.cos_sim(idea_embedding, comp_embedding).item()
        sim_score = max(0.0, min(1.0, sim_score)) # Clamp between 0 and 1
        
        comp["similarity"] = round(sim_score * 100)
        if sim_score > max_similarity:
            max_similarity = sim_score

    # 3. MATHEMATICAL NOVELTY SCORE COMPUTATION
    calculated_novelty_score = round((1.0 - max_similarity) * 100)
    print(f"[SBERT] Computed Mathematical Novelty Score: {calculated_novelty_score}%")

    # 4. GROQ LLM STRATEGIC RECOMMENDATION LAYER (Now requesting 5 points)
    print("[Groq] Generating AI Strategy based on Mathematical Score...")
    context = "".join([f"Company: {c['name']} (Similarity: {c['similarity']}%)\nDescription: {c['desc']}\n\n" for c in all_competitors])

    prompt = f"""
    You are an expert startup analyst. 
    A user proposed this business idea: "{business_idea}"
    
    Our SBERT Semantic Engine has calculated a Novelty Score of {calculated_novelty_score}% based on these real competitors:
    {context}
    
    You MUST provide your response in exactly this formatted structure. 
    INSTRUCTION: You must wrap the single most important sentence in your Market Analysis in == == marks so we can highlight it. (Example: ==The market is highly saturated with UAV systems.==)
    
    **Industry Domain:** [Insert 1-3 word industry category here, like "EdTech" or "AgriTech"]
    **Novelty Score:** {calculated_novelty_score}%
    
    **Market Analysis:**
    [Briefly explain WHY the idea received this novelty score based on the competitors provided. Remember to wrap the key takeaway sentence in == == marks.]
    
    **Actionable Suggestions:**
    **1. Strategic Differentiation:** [Your specific differentiation suggestion here]
    **2. Target Audience Pivot:** [Your specific audience suggestion here]
    **3. Core Technology Focus:** [Your specific feature suggestion here]
    **4. Monetization Strategy:** [Your specific pricing or revenue model suggestion here]
    **5. Go-To-Market Tactic:** [Your specific launch or early-acquisition suggestion here]
    """

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        ai_text = completion.choices[0].message.content
        print("[Success] Full Pipeline Complete!\n")
    except Exception as e:
        print(f"[Groq Error] AI Analysis failed: {e}")
        ai_text = f"**Industry Domain:** UNCATEGORIZED\n**Novelty Score:** {calculated_novelty_score}%\n\nError generating strategy due to API limits."
    
    return {"competitors": {"india": india_list, "global": global_list}, "ai_analysis": ai_text}

@app.route('/')
def home(): return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze(): return jsonify(run_dual_mission_analysis(request.json.get('idea')))

if __name__ == '__main__':
    app.run(debug=True, threaded=True)