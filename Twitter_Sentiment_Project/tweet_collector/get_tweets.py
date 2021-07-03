import tweepy
from tweepy import OAuthHandler, Cursor, API
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
import logging
from config import Twitter # storage for authentification
import pymongo

client = pymongo.MongoClient("mongodb")
db = client.tweets
collection = db.tweet_data




consumer_key = Twitter['consumer_key']
consumer_secret = Twitter['consumer_secret']
access_token = Twitter['access_token']
access_token_secret = Twitter['access_token_secret']

AUTH = tweepy.OAuthHandler(consumer_key, consumer_secret)

## user authentification
AUTH.set_access_token(Twitter['access_token'], Twitter['access_token_secret'])



### SECTION 2: ACCESSING REST API #####
#######################################
## access to REST Api (no streaming)
"""api = tweepy.API(AUTH, wait_on_rate_limit=True)
user = api.me()
logging.critical("connection established with user: " + user.name)


if __name__ == '__main__':
    AUTH = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = API(AUTH)

    cursor = Cursor(
        api.user_timeline,
        id = 'tagesschau',
        tweet_mode = 'extended'
    )

    for status in cursor.items(10):
        text = status.full_text

        # take extended tweets into account
        # TODO: CHECK
        if 'extended_tweet' in dir(status):
            text =  status.extended_tweet.full_text
        if 'retweeted_status' in dir(status):
            r = status.retweeted_status
            if 'extended_tweet' in dir(r):
                text =  r.extended_tweet.full_text

        tweet = {
            'text': text,
            'username': status.user.screen_name,
            'followers_count': status.user.followers_count
        }
        print(tweet)
        collection.insert_one(tweet)"""


### SECTION 3 STREAMING 

class MaxTweetsListener(tweepy.StreamListener):
    
    
    def __init__(self, max_tweets, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_tweets = max_tweets
        self.counter = 0
    
    def on_connect(self):
        logging.critical('CONNECTED')

    def on_data(self, data):
        """Whatever we put in this method defines what is done with
        every single tweet as it is intercepted in real-time"""
        
        t = json.loads(data) # t is just a regular python dictionary.
        
        tweet = {'text': t['text'],
            'username': t['user']['screen_name'],
            'followers_count': t['user']['followers_count']
        }
        collection.insert_one(tweet)
        logging.critical(f' TWEET INCOMING: \n\n\n{tweet["username"]}:{tweet["text"]}\n\n\n')
        
        with open('fetched_tweets.txt',mode='a') as ft:
            ft.write(tweet["text"])
        
        self.counter += 1
        if self.max_tweets == self.counter:
            self.counter=0
            return False
        
    def on_error(self, status_code):
        if status_code == 420:
            logging.error('rate limited')
            #returning False in on_error disconnects the stream
            return False

if __name__ == '__main__':
    #logging.basicConfig(filename='file.log')
    # create a listener object
    max_tweets_listener = MaxTweetsListener(max_tweets=10)
    # setup the stream
    stream = tweepy.Stream(auth=AUTH, listener=max_tweets_listener) 
    # filter the stream
    stream.filter(track=['Euro2021'],languages=['en'])



