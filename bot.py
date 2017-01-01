import os
import pickle
import tweepy
from secret import *
import time
import random
import markovify

# Get raw text as string.
with open("descriptions.txt") as f:
    text = f.read()
# Build the model.
text_model = markovify.Text(text)
# Get pokemon names as list
with open('names.txt', 'rb') as f:
    pkmn_names = pickle.load(f)
# tweepy authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Tweeting Loop
while True:
    tweet = text_model.make_short_sentence(115)
    rand_pkmn = random.randrange(0, 800)
    tweet_with_pkmn = "%s - %s" % (pkmn_names[rand_pkmn], tweet)
    api.update_status(tweet_with_pkmn)
    time.sleep(43200) #wait 12 hours between tweets