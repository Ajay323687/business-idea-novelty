import os
import re
import random
import requests
from dotenv import load_dotenv

# FORCE load environment variables, overriding any cached terminal memory
load_dotenv(override=True)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_groq_key():
    """Dynamically fetch the key and override the system cache."""
    load_dotenv(override=True) # Secondary explicit override
    key = os.getenv("GROQ_API_KEY", "").strip().lstrip('\ufeff')
    return key

def clean_brand_name(raw_title):
    """
    Cleans messy SEO titles from live web searches to extract just the brand name.
    Example: 'Build Web-Apps 10x Faster with AI | WeWeb' -> 'WeWeb'
    """
    if not raw_title:
        return "Unknown Startup"
        
    separators = [' | ', ' - ', ' – ', ' : ', ' — ']
    cleaned_name = raw_title
    
    for sep in separators:
        if sep in cleaned_name:
            parts = cleaned_name.split(sep)
            # The brand name is usually the shortest string in an SEO title
            cleaned_name = min(parts, key=len).strip()
            
    # Fallback to prevent returning massive strings
    return cleaned_name if len(cleaned_name) < 30 else cleaned_name[:27] + "..."


def detect_domain(idea_lower):
    """Detect the business domain from the idea text."""
    domains = [
        ("food tech",        ["food", "restaurant", "meal", "delivery", "cook", "chef", "recipe", "eat"]),
        ("edtech",           ["tutor", "education", "learn", "student", "course", "school", "teach", "skill", "exam"]),
        ("healthtech",       ["health", "medical", "doctor", "fitness", "wellness", "clinic", "patient", "hospital"]),
        ("transport tech",   ["ride", "cab", "transport", "vehicle", "driver", "commute", "bike", "taxi"]),
        ("agritech",         ["farm", "agriculture", "crop", "farmer", "soil", "harvest", "irrigation"]),
        ("fintech",          ["finance", "payment", "bank", "invest", "money", "loan", "crypto", "wallet", "insurance"]),
        ("digital services", ["design", "web", "agency", "creative", "brand", "graphic", "ui", "ux", "develop"]),
        ("AI/ML",            ["ai", "artificial", "machine", "model", "predict", "automate", "nlp", "vision"]),
        ("ecommerce",        ["shop", "store", "buy", "sell", "product", "marketplace", "retail", "commerce"]),
        ("social tech",      ["social", "community", "connect", "network", "chat", "messaging", "friend"]),
        ("SaaS",             ["software", "platform", "tool", "dashboard", "api", "cloud", "saas", "automation"]),
        ("proptech",         ["property", "real estate", "rent", "house", "apartment", "land", "tenant"]),
        ("legaltech",        ["legal", "lawyer", "law", "court", "contract", "compliance", "attorney"]),
        ("hrtech",           ["hiring", "recruitment", "hr", "employee", "workforce", "talent", "payroll"]),
    ]
    for domain, keywords in domains:
        if any(kw in idea_lower for kw in keywords):
            return domain
    return "technology"


def build_groq_prompt(idea, novelty_score, matches, competitor_names, domain):
    """Build a highly dynamic, specific Groq prompt."""
    similar_text = ""
    if matches:
        for m in matches[:3]:
            name = m.get('name', '')
            desc = m.get('description', '')[:120]
            sim  = m.get('similarity', 0)
            similar_text += f"- {name} ({sim:.1f}% similar): {desc}\n"
    else:
        similar_text = "No direct competitors found."

    comp_str = ", ".join(competitor_names) if competitor_names else "no direct competitors"

    if novelty_score >= 80:
        score_context = f"EXTREMELY NOVEL ({novelty_score:.1f}%) — almost no competition exists"
        angle = "focus on speed to market, category creation, and first-mover advantage"
    elif novelty_score >= 65:
        score_context = f"HIGHLY NOVEL ({novelty_score:.1f}%) — very few similar businesses exist"
        angle = "focus on validating demand quickly and defining the category narrative"
    elif novelty_score >= 50:
        score_context = f"MODERATELY NOVEL ({novelty_score:.1f}%) — some competition but clear differentiation room"
        angle = "focus on niche targeting, differentiation from competitors, and distribution"
    elif novelty_score >= 35:
        score_context = f"SOMEWHAT COMMON ({novelty_score:.1f}%) — significant competition exists"
        angle = "focus on specific wedge strategy, underserved segments, and competitor weaknesses"
    else:
        score_context = f"HIGHLY SATURATED ({novelty_score:.1f}%) — very crowded market"
        angle = "focus on extreme specialization, contrarian pricing, and finding gaps competitors ignore"

    prompt = f"""You are a brutally honest Y Combinator partner advising a founder.

BUSINESS IDEA: "{idea}"
DOMAIN: {domain}
NOVELTY SCORE: {score_context}
STRATEGIC ANGLE: {angle}

ACTUAL COMPETITORS FOUND IN MARKET:
{similar_text}

Your task: Write EXACTLY 5 strategic recommendations.

STRICT RULES:
1. ALWAYS mention "{idea}" by name in at least 3 of the 5 points
2. ALWAYS mention at least one real competitor by name: {comp_str}
3. Each recommendation must be SPECIFIC to this exact idea and score of {novelty_score:.1f}%
4. The advice must change based on the novelty score — {novelty_score:.1f}% should feel different from 50% or 80%
5. NO generic startup advice that could apply to any idea
6. Be sharp, direct, like a partner who has seen 1000 pitches
7. Maximum 2 sentences per point
8. No bold, no bullets, no markdown formatting

Output EXACTLY in this format, nothing else:
1. [recommendation]
2. [recommendation]
3. [recommendation]
4. [recommendation]
5. [recommendation]"""

    return prompt


def generate_suggestions(idea, novelty_score=50, matches=None):
    # Fetch the API key dynamically right when the function is called
    api_key = get_groq_key()
    
    print(f"[ai_suggestions] GROQ key loaded: {'YES (len=' + str(len(api_key)) + ')' if api_key else 'NO'}")

    # Clean the names for BOTH the AI and the Frontend
    if matches:
        for m in matches:
            if 'name' in m:
                m['name'] = clean_brand_name(m['name'])
                
    idea_lower       = idea.lower()
    domain           = detect_domain(idea_lower)
    competitor_names = [m.get('name', '') for m in (matches or [])[:3] if m.get('name')]

    if not api_key:
        print("GROQ_API_KEY not found — using smart fallback")
        return smart_fallback(idea, novelty_score, matches, competitor_names, domain)

    prompt = build_groq_prompt(idea, novelty_score, matches, competitor_names, domain)

    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it",
        "mixtral-8x7b-32768",
    ]

    for model in models:
        try:
            print(f"Trying Groq model: {model}")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"You are a Y Combinator-style startup advisor specializing in {domain}. "
                            f"This idea scored {novelty_score:.1f}% novelty. "
                            "Give brutally specific, actionable advice that directly references "
                            "the actual idea and real competitor names. "
                            "Your advice MUST differ based on whether the score is high or low novelty. "
                            "Never give generic advice that could apply to any startup."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.9,
                "max_tokens":  800,
                "top_p":       0.95,
                "seed": random.randint(1, 99999),
            }

            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            print(f"Groq response ({model}): {response.status_code}")

            if response.status_code == 200:
                raw_text    = response.json()["choices"][0]["message"]["content"]
                suggestions = parse_suggestions(raw_text)
                if suggestions and len(suggestions) >= 3:
                    print(f"Got {len(suggestions)} suggestions from {model}")
                    return suggestions
                print(f"Parsing failed for {model}, trying next...")
            elif response.status_code == 401:
                print("Invalid GROQ_API_KEY")
                break
            elif response.status_code == 429:
                print(f"Rate limited on {model}")
                continue
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print(f"Timeout on {model}")
        except Exception as e:
            print(f"Exception with {model}: {e}")

    print("All Groq models failed — using smart fallback")
    return smart_fallback(idea, novelty_score, matches, competitor_names, domain)


def parse_suggestions(text):
    suggestions = []
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = text.strip()

    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < 20:
            continue
        match = re.match(r'^(\d+)[\.\)\:\-\s]+(.+)', line)
        if match:
            content = re.sub(r'\*+', '', match.group(2)).strip()
            if len(content) > 20:
                suggestions.append(content)

    if len(suggestions) < 3:
        suggestions = []
        for s in re.split(r'\n\n|\n(?=\d)', text):
            s = re.sub(r'^\d+[\.\)\:\-\s]+', '', s.strip()).strip()
            s = re.sub(r'\*+', '', s).strip()
            if len(s) > 30:
                suggestions.append(s)

    return suggestions[:5]


def smart_fallback(idea, novelty_score, matches, competitor_names=None, domain=None):
    if not competitor_names:
        competitor_names = [m['name'] for m in (matches or [])[:3]]
    if not domain:
        domain = detect_domain(idea.lower())

    comp_str   = ", ".join(competitor_names) if competitor_names else "existing players in this space"
    comp_first = competitor_names[0] if competitor_names else "your top competitor"
    comp_second = competitor_names[1] if len(competitor_names) > 1 else comp_first

    score = novelty_score
    idea_q = f'"{idea}"'

    if score < 30:
        strategies = [
            [
                f'{idea_q} enters a market where {comp_first} already has strong traction at {score:.0f}% novelty — your only defensible move is hyper-specialisation. Pick one city, one industry vertical, or one customer persona and go 10x deeper than {comp_str} dare to.',
                f"Mine {comp_first}'s 1-star reviews on Google, Trustpilot, and social media — those unresolved complaints are your entire product roadmap for {idea_q}.",
                f'Flip the pricing model: if {comp_str} charge per project, launch {idea_q} on a monthly retainer; if they charge retainer, offer pay-per-outcome to remove all buyer risk.',
                f'At {score:.0f}% novelty, paid ads will bleed you dry competing with {comp_first} — instead own one free distribution channel they ignore, whether WhatsApp groups, LinkedIn DMs, or niche offline events.',
                f'Position {idea_q} as the premium, hands-on alternative to {comp_str} for a high-value segment they treat as unprofitable — boutique always beats scale at the start.',
            ],
            [
                f'With {score:.0f}% novelty, {idea_q} needs a razor-sharp wedge: target the exact customer type {comp_first} loses most often, validate with 10 conversations this week, then build only what that segment needs.',
                f"{comp_first}'s weakest point is almost certainly onboarding or customer support — make {idea_q}'s first 30 days so smooth it becomes your core marketing story.",
                f'Undercut {comp_str} on contract length first, not price — monthly rolling contracts for {idea_q} remove the commitment friction that stops buyers from switching.',
                f'Publish a brutally honest comparison page: {idea_q} vs {comp_first} vs {comp_second} — buyers searching alternatives will find you before they find anyone else.',
                f'At this competition level, partnerships beat cold outreach — find two complementary tools your target customers already pay for and propose a referral deal before building anything new.',
            ],
        ]

    elif score < 50:
        strategies = [
            [
                f'{idea_q} at {score:.0f}% novelty has real room to differentiate — but {comp_first} has momentum. Your fastest path: find where {comp_first} customers complain publicly this week and reach out to them directly.',
                f'Unlike {comp_str} who target everyone, pick one vertical for {idea_q} — legal, healthcare, or D2C brands who need {domain} solutions but feel underserved by generic providers.',
                f'Build one free micro-tool adjacent to {idea_q} that {comp_str} don\'t offer — a calculator, audit template, or scorecard. It generates qualified leads without fighting their ad spend.',
                f'Offer a 45-day money-back guarantee on {idea_q} that {comp_str} don\'t have — in a {score:.0f}% novelty market, de-risking the purchase beats having a marginally better product.',
                f'Run 5 paid pilots of {idea_q} at a 40% discount — real revenue, even discounted, surfaces honest objections that {comp_str} have never had to solve from their earliest customers.',
            ],
            [
                f'At {score:.0f}% novelty, {idea_q} needs a strong point of view — write a contrarian one-page essay on why {comp_first}\'s approach is fundamentally flawed and publish it where your buyers spend time.',
                f'Map every integration {comp_first} and {comp_second} don\'t support, then make {idea_q} the best-connected option in the {domain} stack — integrations are distribution in B2B.',
                f'Offer white-label or agency reseller pricing for {idea_q} — {comp_str} rarely do this well, and agencies bring recurring clients at zero acquisition cost.',
                f'Commission three real case studies from your first {idea_q} users before spending anything on marketing — social proof beats feature lists at this competition level.',
                f'Find the three biggest {domain} communities online, answer questions for 30 days without pitching {idea_q}, then do a transparent "here\'s what I built" post — warm audiences convert 5x better than cold ads.',
            ],
        ]

    elif score < 75:
        strategies = [
            [
                f'{idea_q} scores {score:.0f}% novelty — genuinely differentiated. Before scaling, confirm the gap is real: run 15 user interviews this week specifically asking why they don\'t use {comp_first} for this.',
                f'Since {comp_str} don\'t fully solve this, {idea_q} can define the category — write the "what is this and why it matters now" narrative and publish it before a better-funded team frames the space.',
                f'Launch {idea_q} on Product Hunt and relevant {domain} communities simultaneously — at {score:.0f}% novelty you\'ll get organic press that {comp_str} can\'t easily replicate.',
                f'Raise pre-seed funding now using the novelty angle — a {score:.0f}% novel {domain} idea with weak direct competition is investor-ready with just a one-pager and 5 customer interviews.',
                f'Build your MVP in 6 weeks using no-code tools — the biggest risk at {score:.0f}% novelty is over-engineering something before confirming the market understands what {idea_q} even does.',
            ],
            [
                f'At {score:.0f}% novelty, {idea_q} sits in sweet spot territory — enough competition to prove demand, enough gap to win. Move fast: your window before {comp_first} copies this angle is 12–18 months.',
                f'Partner with one established player from {comp_str} as a white-label or integration partner rather than fighting them — at {score:.0f}% novelty you\'re more useful as an add-on than a direct rival.',
                f'Focus {idea_q}\'s first 90 days entirely on one geography or one industry — depth in a small market beats shallow coverage everywhere when you\'re still finding product-market fit.',
                f'Get three paying customers for {idea_q} before writing a single line of code — at {score:.0f}% novelty the concept is strong enough to pre-sell with just a landing page and a call.',
                f'Apply to {domain}-focused accelerators immediately — a {score:.0f}% novelty score with real differentiation from {comp_str} is exactly what domain-specific funds look for at pre-seed.',
            ],
        ]

    else:
        strategies = [
            [
                f'{idea_q} scores {score:.0f}% novelty — rare territory. Before building anything, validate demand is real: novel doesn\'t mean wanted. Get 10 people to pay even a small amount before writing code.',
                f'With {comp_str} as only loose comparisons, {idea_q} has no established category — you must educate buyers, which means content and community before product. Start a newsletter or podcast this week.',
                f'File a provisional patent for {idea_q} now — at {score:.0f}% novelty the concept has defensive IP value. A provisional costs under ₹5,000 and gives 12 months of protection while you build.',
                f'Raise pre-seed capital immediately — a {score:.0f}% novel {domain} idea is the strongest possible investor story. You don\'t need a product, just evidence of demand and a credible team.',
                f'The biggest risk for {idea_q} isn\'t competition from {comp_str} — it\'s that the market doesn\'t understand the problem yet. Your first 3 months should be 70% market education, 30% product.',
            ],
            [
                f'At {score:.0f}% novelty, {idea_q} is pioneer territory — find 50 people with the exact problem and do the solution manually for them before automating anything. Charge for the manual version first.',
                f'Since {comp_str} are only tangentially related, you\'re not fighting incumbents — you\'re fighting ignorance. Pick the single most compelling use case for {idea_q} and make it undeniably obvious.',
                f'Apply to top accelerators (YC, Antler, Surge) with {idea_q} right now — {score:.0f}% novelty with a clear problem and no direct competition is a strong application, especially in {domain}.',
                f'Build in public from day one — tweet, post, and document every decision behind {idea_q}. At this novelty level, your journey IS your marketing and {comp_str} can\'t copy authenticity.',
                f'Set a hard 8-week deadline to get {idea_q}\'s first paying customer. High novelty ideas die from slow iteration, not competition — speed of learning beats perfection at this stage.',
            ],
        ]

    chosen = random.choice(strategies)
    middle = chosen[1:4]
    random.shuffle(middle)
    return [chosen[0]] + middle + [chosen[4]]

if __name__ == "__main__":
    result = generate_suggestions(
        idea="ai tutor for college students",
        novelty_score=38,
        matches=[
            {"name": "ProfessorAI", "description": "AI tutor for standardized tests", "similarity": 79},
            {"name": "TutorAI", "description": "Interactive educational content platform", "similarity": 78},
            {"name": "Studdy", "description": "AI based tutoring platform for students", "similarity": 60},
        ]
    )
    print("\nSuggestions:")
    for i, s in enumerate(result, 1):
        print(f"  {i}. {s}")