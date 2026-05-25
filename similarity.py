import re
import numpy as np
import requests
import os
import time
import random
from urllib.parse import urlparse
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ddgs import DDGS

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

TLD_TO_FLAG = {
    ".co.uk": ("🇬🇧", "United Kingdom"), ".in": ("🇮🇳", "India"),
    ".uk": ("🇬🇧", "United Kingdom"), ".de": ("🇩🇪", "Germany"),
    ".fr": ("🇫🇷", "France"), ".jp": ("🇯🇵", "Japan"),
    ".au": ("🇦🇺", "Australia"), ".ca": ("🇨🇦", "Canada"),
    ".br": ("🇧🇷", "Brazil"), ".sg": ("🇸🇬", "Singapore"),
    ".nl": ("🇳🇱", "Netherlands"), ".se": ("🇸🇪", "Sweden"),
    ".ae": ("🇦🇪", "UAE"), ".il": ("🇮🇱", "Israel"),
    ".com": ("🇺🇸", "USA"), ".io": ("🇺🇸", "USA"),
    ".ai": ("🇺🇸", "USA"), ".co": ("🇺🇸", "USA"),
    ".app": ("🇺🇸", "USA"), ".net": ("🇺🇸", "USA"),
    ".org": ("🇺🇸", "USA"),
}

INDIAN_BRANDS = {
    "swiggy", "zomato", "flipkart", "meesho", "nykaa", "zepto", "blinkit",
    "bigbasket", "dunzo", "rapido", "ola", "paytm", "phonepe", "groww",
    "zerodha", "upstox", "cleartax", "freshworks", "zoho", "razorpay",
    "byju", "unacademy", "vedantu", "practo", "healthifyme",
    "lenskart", "policybazaar", "acko", "cars24", "spinny", "droom",
    "oyo", "makemytrip", "yatra", "ixigo", "urbanclap", "urban company",
    "cred", "slice", "jupiter", "fi money", "niyo",
}

KNOWN_BRANDS = {
    "webflow": "Webflow", "wix": "Wix", "shopify": "Shopify", "wordpress": "WordPress",
    "canva": "Canva", "figma": "Figma", "notion": "Notion", "airtable": "Airtable",
    "stripe": "Stripe", "paypal": "PayPal", "openai": "OpenAI" 
    # Notice: GitHub is completely removed from here so we can grab repo names!
}

COMPANY_LOCATIONS = {
    # INDIA - Bangalore
    "swiggy": {"lat": 12.9716, "lng": 77.5946, "sector": "Foodtech", "city": "Bangalore", "country": "India"},
    "flipkart": {"lat": 12.9352, "lng": 77.6245, "sector": "Ecommerce", "city": "Bangalore", "country": "India"},
    "meesho": {"lat": 12.9249, "lng": 77.6255, "sector": "Ecommerce", "city": "Bangalore", "country": "India"},
    "zepto": {"lat": 12.9141, "lng": 77.6398, "sector": "Foodtech", "city": "Bangalore", "country": "India"},
    "bigbasket": {"lat": 12.9698, "lng": 77.7499, "sector": "Foodtech", "city": "Bangalore", "country": "India"},
    "dunzo": {"lat": 12.9611, "lng": 77.6446, "sector": "Logistics", "city": "Bangalore", "country": "India"},
    "rapido": {"lat": 12.9220, "lng": 77.6188, "sector": "Transport", "city": "Bangalore", "country": "India"},
    "ola": {"lat": 12.9343, "lng": 77.6044, "sector": "Transport", "city": "Bangalore", "country": "India"},
    "phonepe": {"lat": 12.9279, "lng": 77.6271, "sector": "Fintech", "city": "Bangalore", "country": "India"},
    "groww": {"lat": 12.9348, "lng": 77.6189, "sector": "Fintech", "city": "Bangalore", "country": "India"},
    "zerodha": {"lat": 12.9081, "lng": 77.5855, "sector": "Fintech", "city": "Bangalore", "country": "India"},
    "unacademy": {"lat": 12.9372, "lng": 77.6269, "sector": "Edtech", "city": "Bangalore", "country": "India"},
    "vedantu": {"lat": 12.9121, "lng": 77.6446, "sector": "Edtech", "city": "Bangalore", "country": "India"},
    "healthifyme": {"lat": 12.9654, "lng": 77.6049, "sector": "Healthtech", "city": "Bangalore", "country": "India"},
    "cred": {"lat": 12.9259, "lng": 77.6229, "sector": "Fintech", "city": "Bangalore", "country": "India"},
    "ninjacart": {"lat": 12.9116, "lng": 77.6389, "sector": "Agritech", "city": "Bangalore", "country": "India"},
    "freshworks": {"lat": 12.9716, "lng": 77.5946, "sector": "SaaS", "city": "Bangalore", "country": "India"},
    
    # INDIA - Delhi / NCR
    "zomato": {"lat": 28.4595, "lng": 77.0266, "sector": "Foodtech", "city": "Gurugram", "country": "India"},
    "paytm": {"lat": 28.5355, "lng": 77.3910, "sector": "Fintech", "city": "Noida", "country": "India"},
    "cleartax": {"lat": 28.6139, "lng": 77.2090, "sector": "Fintech", "city": "New Delhi", "country": "India"},
    "lenskart": {"lat": 28.4595, "lng": 77.0266, "sector": "Ecommerce", "city": "Gurugram", "country": "India"},
    "policybazaar": {"lat": 28.4595, "lng": 77.0266, "sector": "Fintech", "city": "Gurugram", "country": "India"},
    "oyo": {"lat": 28.4595, "lng": 77.0266, "sector": "Hospitality", "city": "Gurugram", "country": "India"},
    "makemytrip": {"lat": 28.4595, "lng": 77.0266, "sector": "Travel", "city": "Gurugram", "country": "India"},
    "ixigo": {"lat": 28.4595, "lng": 77.0266, "sector": "Travel", "city": "Gurugram", "country": "India"},
    "blinkit": {"lat": 28.4595, "lng": 77.0266, "sector": "Foodtech", "city": "Gurugram", "country": "India"},
    "cars24": {"lat": 28.4595, "lng": 77.0266, "sector": "Ecommerce", "city": "Gurugram", "country": "India"},

    # INDIA - Mumbai / Pune
    "nykaa": {"lat": 19.0760, "lng": 72.8777, "sector": "Ecommerce", "city": "Mumbai", "country": "India"},
    "dream11": {"lat": 19.0176, "lng": 72.8561, "sector": "Gaming", "city": "Mumbai", "country": "India"},
    "upstox": {"lat": 19.0760, "lng": 72.8777, "sector": "Fintech", "city": "Mumbai", "country": "India"},
    
    # INDIA - Other
    "byju": {"lat": 17.3850, "lng": 78.4867, "sector": "Edtech", "city": "Hyderabad", "country": "India"},
    "zoho": {"lat": 12.8360, "lng": 80.0183, "sector": "SaaS", "city": "Chennai", "country": "India"},
    "practo": {"lat": 12.9716, "lng": 77.5946, "sector": "Healthtech", "city": "Chennai", "country": "India"},

    # GLOBAL - USA
    "uber": {"lat": 37.7749, "lng": -122.4194, "sector": "Transport", "city": "San Francisco", "country": "USA"},
    "slack": {"lat": 37.7749, "lng": -122.4194, "sector": "SaaS", "city": "San Francisco", "country": "USA"},
    "stripe": {"lat": 37.7749, "lng": -122.4194, "sector": "Fintech", "city": "San Francisco", "country": "USA"},
    "figma": {"lat": 37.7749, "lng": -122.4194, "sector": "Design", "city": "San Francisco", "country": "USA"},
    "notion": {"lat": 37.7749, "lng": -122.4194, "sector": "SaaS", "city": "San Francisco", "country": "USA"},
    "anthropic": {"lat": 37.7749, "lng": -122.4194, "sector": "AI/ML", "city": "San Francisco", "country": "USA"},
    "github": {"lat": 37.7749, "lng": -122.4194, "sector": "DevTools", "city": "San Francisco", "country": "USA"},
    "openai": {"lat": 40.7128, "lng": -74.0060, "sector": "AI/ML", "city": "New York", "country": "USA"},
    "coursera": {"lat": 37.4419, "lng": -122.1430, "sector": "Edtech", "city": "Palo Alto", "country": "USA"},
    "udemy": {"lat": 37.3382, "lng": -121.8863, "sector": "Edtech", "city": "San Jose", "country": "USA"},
    "duolingo": {"lat": 40.4406, "lng": -79.9959, "sector": "Edtech", "city": "Pittsburgh", "country": "USA"},
    "paypal": {"lat": 37.3382, "lng": -121.8863, "sector": "Fintech", "city": "San Jose", "country": "USA"},
    "jira": {"lat": 42.3601, "lng": -71.0589, "sector": "DevTools", "city": "Boston", "country": "USA"},
    
    # GLOBAL - Other
    "shopify": {"lat": 43.6510, "lng": -79.3470, "sector": "Ecommerce", "city": "Toronto", "country": "Canada"},
    "canva": {"lat": -33.8688, "lng": 151.2093, "sector": "Design", "city": "Sydney", "country": "Australia"},
}

def extract_brand_from_url(url):
    if not url: return None
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc or parsed.path
        netloc = re.sub(r'^www\.', '', netloc.lower())
        domain_part = netloc.split('.')[0]
        domain_part = re.sub(r'(app|web|get|try|use|go|my|the|best|top)$', '', domain_part)
        domain_part = re.sub(r'^(app|web|get|try|use|go|my|the|best|top)', '', domain_part)
        if domain_part in KNOWN_BRANDS: return KNOWN_BRANDS[domain_part]
        brand = re.sub(r'[-_]', ' ', domain_part).strip().title()
        if len(brand) >= 3 and brand.lower() not in {'home', 'site', 'page', 'online', 'digital', 'tech'}: return brand
    except Exception: pass
    return None

def get_country_from_url(url):
    if not url: return ("🌐", "Global")
    u = url.lower().strip()
    for tld, (flag, country) in sorted(TLD_TO_FLAG.items(), key=lambda x: -len(x[0])):
        if tld + "/" in u or tld + "?" in u or u.endswith(tld): return (flag, country)
    return ("🌐", "Global")

def is_indian_brand(name, url):
    name_lower = (name or "").lower().strip()
    if any(brand in name_lower for brand in INDIAN_BRANDS): return True
    if ".in/" in (url or "").lower() or (url or "").lower().endswith(".in"): return True
    return False

def get_location_data(company_name, country, desc):
    """Retrieves exact coordinates and sector for a company, or generates plausible fallbacks."""
    name_lower = company_name.lower().replace(" ", "")
    
    for brand, data in COMPANY_LOCATIONS.items():
        if brand in name_lower:
            return data

    fallback = {"sector": "Technology", "city": "Unknown"}
    
    sectors = {"Fintech": ["pay", "bank", "invest", "crypto", "finance"], "AI/ML": ["ai", "machine", "data", "intelligence"], "Ecommerce": ["shop", "store", "buy", "sell", "retail"], "Edtech": ["learn", "tutor", "school", "course"], "Healthtech": ["health", "medical", "doctor", "fitness"], "Foodtech": ["food", "delivery", "restaurant", "meal"], "SaaS": ["software", "dashboard", "b2b", "platform"]}
    for s, kws in sectors.items():
        if any(kw in desc.lower() for kw in kws):
            fallback["sector"] = s
            break
            
    if country == "India":
        fallback["lat"] = 20.5937 + random.uniform(-5, 5)
        fallback["lng"] = 78.9629 + random.uniform(-5, 5)
        fallback["country"] = "India"
    elif country == "USA":
        fallback["lat"] = 37.0902 + random.uniform(-5, 5)
        fallback["lng"] = -95.7129 + random.uniform(-10, 10)
        fallback["country"] = "USA"
    else:
        fallback["lat"] = random.uniform(-30, 50)
        fallback["lng"] = random.uniform(-100, 100)
        fallback["country"] = country

    return fallback

SKIP_DOMAINS = [
    "wikipedia.org", "youtube.com", "reddit.com", "twitter.com", "linkedin.com",
    "forbes.com", "techcrunch.com", "businessinsider.com", "g2.com", "capterra.com",
    "quora.com", "stackoverflow.com", "medium.com", "crunchbase.com",
]

def clean_description(text):
    text = re.sub(r'Missing:\s*\S+\s*\|?\s*Show results with:\s*\S+', '', text, flags=re.IGNORECASE)
    text = text.replace('|', ' ')
    return re.sub(r'\s{2,}', ' ', text).strip()

def clean_name(name):
    # Smart extraction for GitHub titles (e.g., "namithisurika/HostelBite: description")
    if "GitHub" in name or "/" in name:
        name = name.replace("GitHub - ", "")
        if ":" in name:
            repo_part = name.split(":")[0] # grabs "username/HostelBite"
            if "/" in repo_part:
                return repo_part.split("/")[-1].strip() # returns just "HostelBite"
    
    # Standard cleanup
    for sep in ["|", "–", "—", " - ", ": "]:
        if sep in name: name = name.split(sep)[0]
    return name.strip()

def search_startups(query):
    results = []
    seen_domains = set()

    with DDGS() as ddgs:
        for q in [f"{query} startup", f"{query} startup India", f"{query} software company"]:
            if len(results) >= 15: break
            try:
                hits = ddgs.text(q, max_results=15)
                for r in hits:
                    raw_title = r.get("title", "").strip()
                    desc = clean_description(r.get("body", ""))
                    url = r.get("href", "")
                    if not raw_title or not desc: continue

                    try: domain_key = urlparse(url).netloc.lower().replace("www.", "")
                    except: domain_key = url[:40]
                    
                    # Allow multiple GitHub repos by treating the specific repo path as the domain key
                    if "github.com" in domain_key:
                        domain_key = urlparse(url).path.lower()

                    if domain_key in seen_domains or any(d in domain_key for d in SKIP_DOMAINS): continue

                    seen_domains.add(domain_key)
                    
                    # Prefer the scraped title for GitHub repos instead of the brand name
                    if "github.com" in url.lower():
                        display_name = clean_name(raw_title)
                    else:
                        display_name = extract_brand_from_url(url) or clean_name(raw_title)
                    
                    results.append({"name": display_name, "description": desc[:300], "url": url})
                time.sleep(1)
            except: pass
    return results

def check_novelty(user_idea):
    results = search_startups(user_idea)
    if not results: return {"novelty_score": 90, "matches": [], "avg_similarity": 0}

    user_emb = model.encode([user_idea])
    descs    = [r["description"] for r in results]
    emb      = model.encode(descs)
    sims     = cosine_similarity(user_emb, emb)[0]

    top_indices = sims.argsort()[-min(5, len(results)):][::-1]

    matches = []
    for i in top_indices:
        sim_percent = round(float(sims[i]) * 100, 2)
        if sim_percent > 5:
            company = results[i]
            url, name, desc = company.get("url", ""), company["name"], company.get("description", "").lower()

            indian_keywords = ["india", "mumbai", "bangalore", "bengaluru", "delhi", "hyderabad", "chennai", "pune", "noida", "gurgaon"]
            
            if is_indian_brand(name, url) or any(kw in desc for kw in indian_keywords):
                flag, country = "🇮🇳", "India"
            else:
                flag, country = get_country_from_url(url)

            loc_data = get_location_data(name, country, desc)

            matches.append({
                "name": name, 
                "description": company["description"], 
                "similarity": sim_percent, 
                "url": url, 
                "flag": flag, 
                "country": country,
                "lat": loc_data["lat"],
                "lng": loc_data["lng"],
                "sector": loc_data["sector"],
                "city": loc_data["city"]
            })

    matches = sorted(matches, key=lambda x: x["similarity"], reverse=True)[:5]
    avg_similarity = np.mean([m["similarity"] for m in matches]) if matches else 0
    novelty_score  = round((1 - avg_similarity / 100) * 100, 2)

    return {"novelty_score": novelty_score, "matches": matches, "avg_similarity": avg_similarity}