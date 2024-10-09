from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import joblib

# Load the pre-trained model
model = joblib.load('stock_model_new.pkl')

# Load the S&P 500 companies data to get sector and industry information
sp500_companies = pd.read_csv('data/sp500_companies.csv', usecols=['Symbol', 'Sector', 'Industry'])

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

    return predicted_change[0]  # Return the predicted percent change

# Example usage
stock_symbol = 'AAPL'
open_price = 150.00
current_headlines = [
    "Apple releases new iPhone models",
    "Market analysts predict strong quarterly earnings for Apple",
    "Concerns over supply chain issues for Apple"
]

predicted_percent_change = predict_stock_change(open_price, stock_symbol, current_headlines)
print(f"Predicted percent change for {stock_symbol}: {predicted_percent_change:.2f}%")
