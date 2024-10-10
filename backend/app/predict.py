from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import joblib
import os
from stocks_info import get_top_headlines

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, 'stock_model_new.pkl')

# Load the pre-trained model
model = joblib.load(model_path)

# Load the S&P 500 companies data to get sector and industry information
sp500_companies_path = os.path.join(BASE_DIR, 'data', 'sp500_companies.csv')
sp500_companies = pd.read_csv(sp500_companies_path, usecols=['Symbol', 'Sector', 'Industry'])

def predict_stock_change(open_price, stock_symbol, headlines):
    # Get industry and sector from the sp500_companies DataFrame
    stock_info = sp500_companies[sp500_companies['Symbol'] == stock_symbol]

    if stock_info.empty:
        raise ValueError(f"Stock symbol '{stock_symbol}' not found in the dataset.")

    industry = stock_info['Industry'].values[0]
    sector = stock_info['Sector'].values[0]

    # Create a new DataFrame to hold the input data
    new_data = pd.DataFrame({
        'Open': [open_price],
        'Headline': [' '.join(headlines)]  # Combine headlines into a single string
    })

    # Sentiment analysis on the headlines
    analyzer = SentimentIntensityAnalyzer()
    new_data['sentiment_score'] = new_data['Headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

    # Separate positive and negative sentiment scores
    new_data['positive_sentiment'] = new_data['sentiment_score'].apply(lambda x: x if x > 0 else 0)
    new_data['negative_sentiment'] = new_data['sentiment_score'].apply(lambda x: x if x < 0 else 0)

    # Create a relevance score based on the stock symbol, industry, and sector
    relevant_words = [stock_symbol.lower(), industry.lower(), sector.lower()]

    positive_words = str(new_data['Headline'].values[0]).lower().split()
    negative_words = str(new_data['Headline'].values[0]).lower().split()

    # Count relevance for positive and negative words
    positive_relevance_count = sum(word in positive_words for word in relevant_words)
    negative_relevance_count = sum(word in negative_words for word in relevant_words)

    total_positive_words = len(positive_words)
    total_negative_words = len(negative_words)

    positive_relevance_score = positive_relevance_count / total_positive_words if total_positive_words > 0 else 0
    negative_relevance_score = negative_relevance_count / total_negative_words if total_negative_words > 0 else 0

    new_data['positive_relevance'] = positive_relevance_score
    new_data['negative_relevance'] = negative_relevance_score

    # Select only the columns that were used during training in the correct order
    input_features = new_data[['Open', 'positive_sentiment', 'negative_sentiment', 'positive_relevance', 'negative_relevance']].copy()  # Create a copy

    # Fill NaN values if any
    input_features.fillna(0, inplace=True)

    # Predict using the trained model
    predicted_change = model.predict(input_features)

    return predicted_change[0], new_data['sentiment_score'].values[0]  # Return the predicted percent change & sentiment score


if __name__ == "__main__":

    stocks = {
        'AAPL': ['Apple', 227.78],
        'NVDA': ['NVIDIA', 131.91],
        'MSFT': ['Microsoft', 415.23],
        'AMZN': ['Amazon', 187.13],
        'META': ['Meta', 587.57],
        'GOOGL': ['Alphabet', 162.11],
        'TSLA': ['Tesla', 241.81],
        'ORCL': ['Oracle', 177.65],
        'AMD': ['AMD', 169.76],
        'NFLX': ['Netflix', 723.29]
    }

    for stock in stocks:
        headlines = get_top_headlines(stocks[stock][0])
        stocks[stock].append(headlines)
        open_price = stocks[stock][1]
        predicted_change, sentiment_score = predict_stock_change(open_price, stock, [article['title'] for article in headlines])
        print(f"Predicted change for {stocks[stock][0]} ({stock}): {predicted_change:.2f}%, with a sentiment score of {sentiment_score:.2f}")
