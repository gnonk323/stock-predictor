import requests
import time
# from app.predict import *


# Alpha Vantage API key
ALPHA_API_KEY = '96OEKSPVHU9ET4JC'
ALPHA_BASE_URL = 'https://www.alphavantage.co/query'

NEWS_API_KEY = '5f6334174d7e439ca4179367e1175217'
NEWS_BASE_URL = 'https://newsapi.org/v2/everything'


def get_stock_open_price(symbol):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'apikey': ALPHA_API_KEY
    }
    response = requests.get(ALPHA_BASE_URL, params=params)
    data = response.json()
    
    # Extracting the latest open price from the time series data
    try:
        latest_time = list(data['Time Series (1min)'].keys())[0]
        open_price = data['Time Series (1min)'][latest_time]['1. open']
        return open_price
    except KeyError:
        return f"Error: Could not retrieve data for {symbol}"


def get_top_headlines(query):
    params = {
        'q': query,
        'language': 'en',
        'sortBy': 'relevancy',
        'apiKey': NEWS_API_KEY
    }
    response = requests.get(NEWS_BASE_URL, params=params)
    data = response.json()

    # Extract the top 3 headlines if available
    try:
        articles = data['articles'][:3]  # Fetch top 3 articles
        return articles
    except KeyError:
        return f"Error: Could not retrieve news for {query}"
    

# testing
if __name__ == "__main__":
    aapl_open_price = get_stock_open_price('AAPL')
    print(f"AAPL open price: {aapl_open_price}")
    print(f"type: {type(aapl_open_price)}")