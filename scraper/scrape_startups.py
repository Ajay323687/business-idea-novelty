import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_startups():
    startups = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # ── 1. Crunchbase Discover (public HTML) ──
    print("🔍 Scraping Crunchbase...")
    try:
        url = "https://www.crunchbase.com/discover/organization.companies"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("a", class_="cb-overflow-ellipsis")
        for card in cards[:50]:
            name = card.get_text(strip=True)
            if name:
                startups.append({"idea_name": name, "category": "Technology", "idea_text": name})
        print(f"  → Got {len(startups)} from Crunchbase")
    except Exception as e:
        print(f"  ❌ Crunchbase: {e}")

    # ── 2. Wikipedia List of Startups ──
    print("🔍 Scraping Wikipedia startup list...")
    try:
        url = "https://en.wikipedia.org/wiki/List_of_largest_technology_company_layoffs"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table", class_="wikitable")
        for table in tables:
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all(["td", "th"])
                if cols:
                    name = cols[0].get_text(strip=True)
                    if name and len(name) > 1:
                        startups.append({
                            "idea_name": name,
                            "category": "Technology",
                            "idea_text": f"{name} is a technology company."
                        })
        print(f"  → Total so far: {len(startups)}")
    except Exception as e:
        print(f"  ❌ Wikipedia: {e}")

    # ── 3. Hacker News Show HN posts (public API) ──
    print("🔍 Scraping Hacker News Show HN...")
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        r = requests.get(url, headers=headers, timeout=10)
        story_ids = r.json()[:100]

        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                sr = requests.get(story_url, headers=headers, timeout=5)
                story = sr.json()
                title = story.get("title", "")
                if title and ("Show HN" in title or "startup" in title.lower()):
                    clean_title = title.replace("Show HN:", "").replace("Show HN", "").strip()
                    if clean_title:
                        startups.append({
                            "idea_name": clean_title[:60],
                            "category": "Technology",
                            "idea_text": clean_title
                        })
                time.sleep(0.1)
            except:
                continue
        print(f"  → Total so far: {len(startups)}")
    except Exception as e:
        print(f"  ❌ HackerNews: {e}")

    # ── 4. GitHub Trending (public) ──
    print("🔍 Scraping GitHub Trending...")
    try:
        url = "https://github.com/trending"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        repos = soup.find_all("p", class_="col-9")
        names = soup.find_all("h2", class_="h3")
        for name, desc in zip(names, repos):
            n = name.get_text(strip=True).replace("\n", "").replace(" ", "")
            d = desc.get_text(strip=True)
            if n and d:
                startups.append({
                    "idea_name": n,
                    "category": "Open Source",
                    "idea_text": d
                })
        print(f"  → Total so far: {len(startups)}")
    except Exception as e:
        print(f"  ❌ GitHub: {e}")

    # ── Save ──
    if startups:
        df = pd.DataFrame(startups)
        df = df.drop_duplicates(subset=["idea_name"])
        df = df[df["idea_text"].str.len() > 10]
        df.to_csv("data/startups.csv", index=False)
        print(f"\n✅ Saved {len(df)} startups to data/startups.csv")
        print(df.head(10))
    else:
        print("❌ No data scraped!")

if __name__ == "__main__":
    scrape_startups()