import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


# Import stock dataset (2010 - 2024)
sp500_stocks = pd.read_csv('sp500_stocks.csv', usecols=['Symbol', 'Date', 'Open', 'Close'])
sp500_companies = pd.read_csv('sp500_companies.csv', usecols=['Symbol', 'Shortname', 'Longname', 'Sector', 'Industry'])


stock_df = pd.merge(sp500_stocks, sp500_companies, on='Symbol', how='inner')

# Import news dataset (2012-2022)
news_df = pd.read_json('News_Category_Dataset_v3.json', lines=True)

# Only include data from overlapping years (2012-2022)
stock_df['Date'] = pd.to_datetime(stock_df['Date'])
news_df['date'] = pd.to_datetime(news_df['date'])
stock_df = stock_df[(stock_df['Date'] >= '2012-01-01') & (stock_df['Date'] < '2022-01-01')]

# EDITING STOCK DATAFRAME
# Add percent change column to stock dataframe
stock_df['Percentchange'] = ((stock_df['Close'] - stock_df['Open']) / stock_df['Open']) * 100


# EDITING NEWS DATAFRAME
# Drop irrelevant columns
news_columns_to_drop = ['link', 'authors', 'short_description', 'category']
news_df.drop(columns=news_columns_to_drop, inplace=True)

# Add sentiment score
analyzer = SentimentIntensityAnalyzer()
news_df['sentiment_score'] = news_df['headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

# Separate positive and negative sentiment scores
news_df['positive_sentiment'] = news_df['sentiment_score'].apply(lambda x: x if x > 0 else 0)
news_df['negative_sentiment'] = news_df['sentiment_score'].apply(lambda x: x if x < 0 else 0)

# Group by date and aggregate
news_df = news_df.groupby('date').agg(
    positive_sentiment=('positive_sentiment', 'sum'),
    negative_sentiment=('negative_sentiment', 'sum'),
    positive_headline=('headline', lambda x: ' '.join(h for h, s in zip(x, news_df['sentiment_score']) if s > 0)),
    negative_headline=('headline', lambda x: ' '.join(h for h, s in zip(x, news_df['sentiment_score']) if s < 0))
).reset_index()

# COMBINE STOCK AND NEWS DATAFRAMES
final_df = pd.merge(stock_df, news_df, left_on='Date', right_on='date', how='inner')
final_df.drop(columns=['date'], inplace=True)


# Function to calculate relevance of stock to headlines
def calculate_relevance(row):
    relevant_words = [row['Symbol'], row['Shortname'], row['Longname'], row['Sector'], row['Industry']]
    
    # Tokenizing the headlines
    positive_words = str(row['positive_headline']).lower().split()
    negative_words = str(row['negative_headline']).lower().split()

    # Count occurrences of relevant words in positive and negative headlines
    positive_relevance_count = sum(word.lower() in positive_words for word in relevant_words)
    negative_relevance_count = sum(word.lower() in negative_words for word in relevant_words)
    
    # Normalize by the length of total words in each headline
    total_positive_words = len(positive_words)
    total_negative_words = len(negative_words)
    
    # Avoid division by zero
    positive_relevance_score = positive_relevance_count / total_positive_words if total_positive_words > 0 else 0
    negative_relevance_score = negative_relevance_count / total_negative_words if total_negative_words > 0 else 0

    return pd.Series([positive_relevance_score, negative_relevance_score])

# Apply the function to each row
final_df[['positive_relevance', 'negative_relevance']] = final_df.apply(calculate_relevance, axis=1)

# Dataframe to be trained by the model
model_df = final_df.drop(columns=['Date', 'Symbol', 'Shortname', 'Longname', 'Sector', 'Industry', 'positive_headline', 'negative_headline', 'Close'])

# Fill NaN values with the mean of the column before splitting
model_df.fillna(model_df.mean(), inplace=True)

# Now split the data into features (X) and target (y)
X = model_df.drop(columns=['Percentchange'])
y = model_df['Percentchange']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Training different models to evaluate best (commented out after evaluation)
"""
# Initialize models
models = {
    'Linear Regression': LinearRegression(),
    'Decision Tree': DecisionTreeRegressor(),
    'Random Forest': RandomForestRegressor(),
    'Gradient Boosting': GradientBoostingRegressor()
}

results = {}


# Train and evaluate models
for name, model in models.items():
    model.fit(X_train, y_train) 
    y_pred = model.predict(X_test)  
    
    # Evaluate performance
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    results[name] = {'MAE': mae, 'R2': r2}

# Print results
for name, metrics in results.items():
    print(f"{name}: MAE = {metrics['MAE']}, R2 = {metrics['R2']}")
"""

# Found that Gradient Boosting performed best with the lowest MAE and highest R2, so will use it as our model
model = GradientBoostingRegressor()
model.fit(X_train, y_train) 

# Save model to be used (commented out after saving)
#joblib.dump(model, 'stock_model_new.pkl')



 





