import requests
import os
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
TICKER = "AAPL"
COMPANY_NAME = '"Apple Inc" OR "Apple stock" OR AAPL'

def fetch_headlines(query, api_key):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    analyzer = SentimentIntensityAnalyzer()
    data = fetch_headlines(COMPANY_NAME, API_KEY)
    articles = data.get("articles", [])
    print(f"Found {len(articles)} articles for {COMPANY_NAME}")
    for article in articles[:10]:
        title = article['title']
        score = analyzer.polarity_scores(title)
        compound = score['compound']
        print(f"[{compound:+.2f}] {title}")