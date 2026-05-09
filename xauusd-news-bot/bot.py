import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SENT_FILE = "sent_news.json"

HIGH_IMPACT_KEYWORDS = [
    "fomc",
    "nfp",
    "nonfarm payrolls",
    "cpi",
    "ppi",
    "federal reserve",
    "powell",
    "interest rate",
    "inflation",
    "gdp",
    "unemployment",
    "retail sales",
    "xauusd",
    "gold",
    "usd",
    "ict"
]


def load_sent_news():
    if not os.path.exists(SENT_FILE):
        return []
    try:
        with open(SENT_FILE, "r") as file:
            return json.load(file)
    except:
        return []


def save_sent_news(sent_news):
    with open(SENT_FILE, "w") as file:
        json.dump(sent_news, file)


def is_relevant(title, description):
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in HIGH_IMPACT_KEYWORDS)


def classify_impact(title):
    title_lower = title.lower()

    if any(word in title_lower for word in ["fomc", "nfp", "cpi", "interest rate", "powell"]):
        return "🔴 HIGH IMPACT"
    elif any(word in title_lower for word in ["gdp", "ppi", "retail sales", "usd"]):
        return "🟠 MEDIUM IMPACT"
    return "🟡 MARKET NEWS"

def fetch_marketaux_news():
    now = datetime.utcnow()
    recent = now - timedelta(days=3)
    published_after = recent.strftime("%Y-%m-%dT%H:%M")

    search_query = (
        "gold OR xauusd OR fomc OR nfp OR cpi OR ppi OR federal reserve OR "
        "powell OR inflation OR usd OR interest rate OR ict"
    )

    url = (
        f"https://api.marketaux.com/v1/news/all?"
        f"search={search_query}"
        f"&language=en"
        f"&limit=15"
        f"&sort=published_desc"
        f"&published_after={published_after}"
        f"&api_token={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    return data.get("data", [])

def send_discord_embed(article):
    title = article.get("title", "No title")
    description = article.get("description", "No description")
    url = article.get("url", "")
    source = article.get("source", "Unknown")
    published_at = article.get("published_at", "Unknown")

    impact = classify_impact(title)

    embed = {
        "title": f"{impact} | XAUUSD NEWS",
        "description": f"**{title}**\n\n{description[:500]}",
        "url": url,
        "color": 16766720,
        "fields": [
            {
                "name": "Source",
                "value": source,
                "inline": True
            },
            {
                "name": "Published",
                "value": published_at,
                "inline": True
            },
            {
                "name": "Market Focus",
                "value": "Gold / USD / Macro",
                "inline": True
            }
        ],
        "footer": {
            "text": "XAUUSD Institutional News Bot"
        }
    }

    payload = {
        "embeds": [embed]
    }

    requests.post(WEBHOOK_URL, json=payload)

def main():
    sent_news = load_sent_news()
    articles = fetch_marketaux_news()

    updated_sent = sent_news.copy()
    sent_count = 0

    for article in articles:
        url = article.get("url")
        title = article.get("title", "")
        description = article.get("description", "")

        if not url or url in sent_news:
            continue

        if not is_relevant(title, description):
            continue

        send_discord_embed(article)
        updated_sent.append(url)
        sent_count += 1

        if sent_count >= 5:
            break

    updated_sent = updated_sent[-300:]
    save_sent_news(updated_sent)

    print(f"Sent {sent_count} new articles.")


if __name__ == "__main__":
    main()
