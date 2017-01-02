import os
import pickle
import tweepy
from markovbot import MarkovBot
from secret import *
import time
import random

# Get raw text as string.
with open("descriptions.txt") as f:
    text = f.read()
# Get pokemon names as list
with open('names.txt', 'rb') as f:
    pkmn_names = pickle.load(f)
# tweepy authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
# MarkovBot creation
bot = MarkovBot()
dirname = os.path.dirname(os.path.abspath(__file__))
source = os.path.join(dirname, 'descriptions.txt')
bot.read(source)

# Tweeting Loop
while True:
    # Generate random pkmn name
    rand_pkmn = random.randrange(0, 800)
    pkmn = pkmn_names[rand_pkmn]
    # Generate tweet containing at most 20 words (checks for max tweet length)
    tweet = bot.generate_text(20)
    while len(tweet) > 120:
        tweet = bot.generate_text(20)
    tweet_with_pkmn = "%s - %s" % (pkmn, tweet)
    # Publish tweet
    api.update_status(tweet_with_pkmn)
    time.sleep(43200) #wait 12 hours between tweets