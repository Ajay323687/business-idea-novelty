import requests
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_suggestions(idea, novelty_score=50, matches=None):
    similar_text = ""
    if matches:
        for m in matches[:3]:
            similar_text += f"- {m['name']}: {m['description'][:80]}\n"
    else:
        similar_text = "No close competitors found"
    
    if novelty_score >= 75:
        score_context = "HIGHLY NOVEL - very few competitors exist"
    elif novelty_score >= 50:
        score_context = "MODERATELY NOVEL - some competition exists"
    elif novelty_score >= 30:
        score_context = "SOMEWHAT COMMON - significant competition"
    else:
        score_context = "HIGHLY SIMILAR - market is very saturated"
    
    prompt = f"""You are an expert startup business advisor.
Business Idea: {idea}
Novelty Score: {novelty_score}% ({score_context})
Similar Companies Already Exist:
{similar_text}
Give exactly 5 specific actionable recommendations for THIS business idea.
Make each recommendation specific to this idea - not generic advice.
Format as numbered list 1. 2. 3. 4. 5.
Keep each point to 1-2 sentences only."""
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert startup advisor who gives specific, actionable business recommendations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Groq Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"]
            print("Got AI suggestions!")
            print(f"Raw text: {text[:300]}")
            suggestions = parse_suggestions(text)
            if suggestions:
                return suggestions
        else:
            print(f"Groq error: {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print("Using fallback suggestion")
    return fallback_suggestions(novelty_score)

def parse_suggestions(text):
    suggestions = []
    text = text.replace("**", "")
    
    lines = text.strip().split("\n")
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 15:
            continue
        if line[0].isdigit():
            if len(line) > 2 and line[1] in ".):":
                clean = line[2:].strip()
            elif len(line) > 3 and line[2] in ".):":
                clean = line[3:].strip()
            else:
                clean = line
            clean = clean.replace("*", "").strip()
            if len(clean) > 15:
                suggestions.append(clean)
    
    return suggestions[:5]

def fallback_suggestions(novelty_score):
    if novelty_score < 30:
        return [
            "Market is heavily saturated - find a very specific niche to dominate",
            "Focus on an underserved geographic region your competitors ignore",
            "Add a unique AI or technology angle that competitors don't have",
            "Target a specific customer segment that existing players overlook",
            "Consider pivoting to a related but less crowded market space"
        ]
    elif novelty_score < 60:
        return [
            "Your idea has potential - differentiate strongly on user experience",
            "Find a unique pricing model that disrupts how competitors charge",
            "Build for a specific community or demographic as your beachhead market",
            "Combine your idea with emerging technology like AI for a competitive edge",
            "Focus on one geography first and dominate before expanding further"
        ]
    else:
        return [
            "Highly novel idea - validate with real users as quickly as possible",
            "Consider filing for a patent or trademark to protect your concept",
            "Build an MVP fast before others spot and enter this opportunity",
            "Educate your market - novelty means you need to create awareness first",
            "Seek early adopters in niche communities to build initial traction"
        ]

if __name__ == "__main__":
    result = generate_suggestions(
        idea="food delivery for pets",
        novelty_score=72,
        matches=[{"name": "PetPlate", "description": "Fresh dog food delivery service", "similarity": 45}]
    )
    print("\nSuggestions:")
    for i, s in enumerate(result, 1):
        print(f"  {i}. {s}")