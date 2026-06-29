import requests
import os
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
from datetime import datetime, timedelta
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

def get_price_data(ticker, days_back=30):
    end = datetime.now()
    start = end - timedelta(days=days_back)
    data = yf.download(ticker, start=start, end=end)
    return data

if __name__ == "__main__":
    analyzer = SentimentIntensityAnalyzer()
    data = fetch_headlines(COMPANY_NAME, API_KEY)
    articles = data.get("articles", [])
    print(f"Found {len(articles)} articles for {COMPANY_NAME}")

    sentiment_records = []
    for article in articles[:10]:
        title = article['title']
        published = article['publishedAt'][:10]
        score = analyzer.polarity_scores(title)
        compound = score['compound']
        sentiment_records.append({"date": published, "title": title, "compound": compound})
        print(f"[{compound:+.2f}] {published} | {title}")

    import pandas as pd
    sentiment_df = pd.DataFrame(sentiment_records)
    daily_sentiment = sentiment_df.groupby("date")["compound"].mean().reset_index()
    print("\n--- Daily Average Sentiment ---")
    print(daily_sentiment)

    print("\n--- Price Data ---")
    prices = get_price_data(TICKER, days_back=60)
    print(prices.tail())

    prices_reset = prices.reset_index()
    prices_reset.columns = prices_reset.columns.get_level_values(0)
    prices_reset["date"] = prices_reset["Date"].dt.strftime("%Y-%m-%d")

    daily_sentiment["date"] = pd.to_datetime(daily_sentiment["date"])
    prices_reset["date"] = pd.to_datetime(prices_reset["date"])

    daily_sentiment = daily_sentiment.sort_values("date")
    prices_reset = prices_reset.sort_values("date")

    merged = pd.merge_asof(daily_sentiment, prices_reset, on="date", direction="backward")
    print("\n--- Merged Sentiment + Price ---")
    print(merged[["date", "compound", "Close"]])
