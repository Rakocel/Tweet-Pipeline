import time
import pymongo
from sqlalchemy import create_engine, exc
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

time.sleep(5)  # seconds

# Establish a connection to the MongoDB server
client = pymongo.MongoClient("mongodb")

# Select the database you want to use withing the MongoDB server
db = client.tweets

# Select the collection of documents you want to use withing the MongoDB database
collection = db.tweet_data

print(collection)


pg = create_engine('postgresql://postgres:postgres@postgresdb_container:5432/db_postgres', echo=True)

pg.execute('''
    DROP TABLE IF EXISTS tweets;
    ''')

pg.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
    text VARCHAR(500),
    sentiment_eva VARCHAR,
    sentiment NUMERIC);
''')


entries = collection.find()
s  = SentimentIntensityAnalyzer()
for e in entries:
    text = e['text']
    
    sentiment = s.polarity_scores(e['text'])
    score = sentiment['compound']
    print(sentiment)

    if score > 0.05:
        sentiment_eva = 'positive'
    elif score < -0.05:
        sentiment_eva= 'negative'
    else:
        sentiment_eva= 'neutral'

    query = "INSERT INTO tweets VALUES (%s, %s, %s);"
    pg.execute(query, (text, sentiment_eva, score))