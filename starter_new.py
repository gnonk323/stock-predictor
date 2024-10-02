import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

 
# import stock dataset (2010 - 2024)
sp500_stocks = pd.read_csv('sp500_stocks.csv')
sp500_companies = pd.read_csv('sp500_companies.csv')
sp500_index = pd.read_csv('sp500_index.csv')

stock_df = pd.merge(sp500_stocks, sp500_companies, on='Symbol', how='inner')
stock_df = pd.merge(stock_df, sp500_index, on='Date', how='inner')


# import news dataset (2012-2022)
news_df = pd.read_json('News_Category_Dataset_v3.json', lines=True)


# only include data from overlapping years (2012-2022)
stock_df['Date'] = pd.to_datetime(stock_df['Date'])
news_df['date'] = pd.to_datetime(news_df['date'])
stock_df = stock_df[(stock_df['Date'] >= '2012-01-01') & (stock_df['Date'] < '2022-01-01')]




# EDITING STOCK DATAFRAME

# Add percent change column to stock dataframe
stock_df['Percentchange'] = ((stock_df['Close'] - stock_df['Open']) / stock_df['Open']) * 100

# drop irrelevant columns
columns_to_drop = ['Adj Close', 'Close', 'High', 'Low', 'Exchange', 'Marketcap', 'Ebitda', 'Currentprice',
                   'Revenuegrowth', 'City', 'State', 'Country', 'Fulltimeemployees', 'Longbusinesssummary', 'Weight']
stock_df.drop(columns=columns_to_drop, inplace=True)



# EDITING NEWS DATAFRAME

# drop irrelevant columns
news_columns_to_drop = ['link', 'authors', 'short_description', 'category']
news_df.drop(columns=news_columns_to_drop, inplace=True)

# add sentiment score
analyzer = SentimentIntensityAnalyzer()
news_df['sentiment_score'] = news_df['headline'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

# seperate positive and negative sentiment scores
news_df['positive_sentiment'] = news_df['sentiment_score'].apply(lambda x : x if x > 0 else 0)
news_df['negative_sentiment'] = news_df['sentiment_score'].apply(lambda x : x if x < 0 else 0)


# group by date, include a total positive and negative sentiment score, and a total positive and negative headline to check 
#   relevance of specific stock

news_df = news_df.groupby('date').agg(
    positive_sentiment = ('positive_sentiment', 'sum'),
    negative_sentiment = ('negative_sentiment', 'sum'),
    positive_headline = ('headline', lambda x: ' '.join(h for h, s in zip(x, news_df['sentiment_score']) if s > 0)),
    negative_headline = ('headline', lambda x: ' '.join(h for h, s in zip(x, news_df['sentiment_score']) if s < 0))
    ).reset_index()



# COMBINE STOCK AND NEWS DATAFRAMES

final_df = pd.merge(stock_df, news_df, left_on='Date', right_on='date', how='inner')
final_df.drop(columns=['date'], inplace=True)

# TEST
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

# Scale the relevance scores between 0 and 1
final_df['positive_relevance'] = np.clip(final_df['positive_relevance'], 0, 1)
final_df['negative_relevance'] = np.clip(final_df['negative_relevance'], 0, 1)

"""
# determine relevance of stock to the postive and negative headline
final_df['positive_relevance'] = 
final_df['negative_relevance'] = 

# finally, determine relevant positive score and relevant negative score
final_df['relevant_positive_score'] = 
final_df['relevant_negative_score'] = 
"""

"""
print(stock_df.head())
print(news_df.head())
print("stock columns: ", stock_df.columns)
print("news columns: ", news_df.columns)
"""

print(final_df.head())
print(final_df.sort_values(by='positive_relevance', ascending=False))
print("final columns", final_df.columns)

df_filtered = final_df[['positive_sentiment', 'negative_sentiment', 'Percentchange']]

# Display the filtered DataFrame
print(df_filtered.head())







