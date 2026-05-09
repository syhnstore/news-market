import requests
import schedule
import time

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def get_gold_news():
    url = (
        f"https://api.marketaux.com/v1/news/all?"
        f"search=gold OR xauusd OR federal reserve OR inflation OR usd OR interest rates"
        f"&language=en"
        f"&limit=3"
        f"&api_token={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    articles = data.get("data", [])

    news_list = []

    for article in articles:
        title = article.get("title")
        source = article.get("source")
        link = article.get("url")
        published = article.get("published_at")

        message = (
            f"🟡 **XAUUSD Market News** 🟡\n"
            f"**{title}**\n"
            f"Source: {source}\n"
            f"Date: {published}\n"
            f"{link}"
        )

        news_list.append(message)

    return news_list

def send_discord():
    news = get_gold_news()

    for item in news:
        payload = {"content": item}
        requests.post(WEBHOOK_URL, json=payload)
        time.sleep(2)

schedule.every(5).minutes.do(send_discord)

print("XAUUSD Bot Running...")

send_discord()

while True:
    schedule.run_pending()
    time.sleep(1)