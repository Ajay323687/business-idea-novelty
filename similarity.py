import re
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# ── NOISE DOMAINS ──
SKIP_DOMAINS = [
    "youtube.com", "instagram.com", "facebook.com", "twitter.com",
    "reddit.com", "wikipedia.org", "linkedin.com", "tiktok.com",
    "pinterest.com", "quora.com", "medium.com", "forbes.com",
    "techcrunch.com", "businessinsider.com", "inc.com", "entrepreneur.com",
    "bloomberg.com", "reuters.com", "bbc.com", "cnn.com",
    "amazon.com", "flipkart.com", "google.com", "yahoo.com",
    "news.ycombinator.com", "paulgraham.com", "hackernews.com",
    "cloudflare.com", "w3schools.com", "stackoverflow.com"
]

# ── NOISE TITLES ──
SKIP_TITLES = [
    "hacker news", "y combinator", "show hn", "ask hn",
    "how to", "what is", "list of", "guide", "review",
    "tutorial", "course", "free", "download", "buy", "cheap",
    "price", "cost", "jobs", "career", "news", "article",
    "blog", "forum", "wiki", "invisible text", "translation tool",
    "test", "moved permanently", "access crunchbase", "using the api",
    "yc startup library", "library"
]

# ── STARTUP KEYWORDS ──
STARTUP_KEYWORDS = [
    "startup", "platform", "app", "service", "solution", "company",
    "software", "tool", "marketplace", "saas", "founded", "funding",
    "series", "seed", "raises", "venture", "product", "launch",
    "users", "customers", "business", "enterprise", "api", "cloud",
    "provides", "offers", "helps", "enables", "connects", "delivers"
]

def fix_spaces(text):
    # Fix missing spaces between words (joined words)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Fix missing space after punctuation
    text = re.sub(r'([.,!?])([A-Za-z])', r'\1 \2', text)
    # Fix words joined without space before common words
    common = ['and','the','is','are','for','with','that','this',
              'has','was','from','into','their','which','when',
              'connecting','providing','offering','platform','service',
              'delivery','based','online','local','users','customers']
    for word in common:
        text = re.sub(rf'([a-z])({word})', rf'\1 \2', text, flags=re.IGNORECASE)
    # Fix multiple spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()

def clean_name(name):
    noise = [
        " Company Profile & Funding", "Company Profile & Funding",
        "Profile & Funding", "& Funding",
        " - Crunchbase", "| Crunchbase", " | Crunchbase",
        " | YC", "| Y Combinator", " | Y Combinator",
        " - Product Hunt", "| Product Hunt", " | Product Hunt",
        " on Product Hunt", " - AngelList", " | AngelList",
        " Company Profile", " - Startup", "- Startup"
    ]
    for n in noise:
        name = name.replace(n, "")
    return name.strip()


def is_valid_result(name, description, url=""):
    name_lower = name.lower()
    desc_lower = description.lower()

    # Skip noise domains
    for domain in SKIP_DOMAINS:
        if domain in url.lower():
            return False

    # Skip noise titles
    for word in SKIP_TITLES:
        if word in name_lower:
            return False

    # Skip short descriptions
    if len(description) < 40:
        return False

    # Skip invisible/test content
    if "invisible" in desc_lower or "translation tool" in desc_lower:
        return False

    # Skip moved permanently / error pages
    if "moved permanently" in desc_lower or "403" in desc_lower:
        return False

    # Must have at least one startup keyword
    return any(kw in desc_lower for kw in STARTUP_KEYWORDS)


def search_startups(query, max_results=15):
    print(f"🔍 Searching: {query}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    raw_results = []

    # ── PRIMARY SEARCH ──
    search_query = f"{query} startup site:producthunt.com OR site:crunchbase.com OR site:angellist.com"
    url = f"https://html.duckduckgo.com/html/?q={search_query}"

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for result in soup.find_all("div", class_="result__body")[:max_results]:
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")
            url_tag = result.find("a", class_="result__url")

            if title_tag and snippet_tag:
                name = clean_name(title_tag.get_text(strip=True))
                description = fix_spaces(snippet_tag.get_text(strip=True))
                link = url_tag.get_text(strip=True) if url_tag else ""

                if is_valid_result(name, description, link):
                    raw_results.append({
                        "name": name,
                        "description": description,
                        "url": link
                    })

        print(f"  → Primary: {len(raw_results)} results")

    except Exception as e:
        print(f"  ❌ Primary error: {e}")

    # ── FALLBACK SEARCH ──
    if len(raw_results) < 3:
        print("  → Trying fallback...")
        try:
            fallback_query = f"{query} company founded app platform service"
            url2 = f"https://html.duckduckgo.com/html/?q={fallback_query}"
            r2 = requests.get(url2, headers=headers, timeout=10)
            soup2 = BeautifulSoup(r2.text, "html.parser")

            for result in soup2.find_all("div", class_="result__body")[:max_results]:
                title_tag = result.find("a", class_="result__a")
                snippet_tag = result.find("a", class_="result__snippet")
                url_tag = result.find("a", class_="result__url")

                if title_tag and snippet_tag:
                    name = clean_name(title_tag.get_text(strip=True))
                    description = fix_spaces(snippet_tag.get_text(strip=True))
                    link = url_tag.get_text(strip=True) if url_tag else ""

                    if is_valid_result(name, description, link):
                        if not any(r["name"] == name for r in raw_results):
                            raw_results.append({
                                "name": name,
                                "description": description,
                                "url": link
                            })

            print(f"  → After fallback: {len(raw_results)} results")

        except Exception as e:
            print(f"  ❌ Fallback error: {e}")

    return raw_results


def check_novelty(user_idea):
    results = search_startups(user_idea)

    if not results:
        return {
            "novelty_score": 92.0,
            "matches": [],
            "avg_similarity": 8.0,
            "message": "No similar startups found — very novel idea!"
        }

    # Encode
    user_embedding = model.encode([user_idea])
    descriptions = [r["description"] for r in results]
    result_embeddings = model.encode(descriptions)

    # Cosine similarity
    similarities = cosine_similarity(user_embedding, result_embeddings)[0]

    # Top 5
    top_n = min(5, len(results))
    top_indices = similarities.argsort()[-top_n:][::-1]
    avg_similarity = float(np.mean(similarities[top_indices]))
    novelty_score = round((1 - avg_similarity) * 100, 2)

    # Build matches — only meaningful ones (>15%)
    matches = []
    for i in top_indices:
        sim_percent = round(float(similarities[i]) * 100, 2)
        if sim_percent > 15:
            matches.append({
                "name": results[i]["name"],
                "description": results[i]["description"],
                "similarity": sim_percent
            })

    return {
        "novelty_score": novelty_score,
        "matches": matches,
        "avg_similarity": round(avg_similarity * 100, 2)
    }


if __name__ == "__main__":
    result = check_novelty("food delivery for street vendors")
    print(f"\n🎯 Novelty Score: {result['novelty_score']}%")
    for m in result["matches"]:
        print(f"  • {m['name']} — {m['similarity']}% — {m['description'][:80]}")