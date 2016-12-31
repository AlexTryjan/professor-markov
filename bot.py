import os
import pickle
from markovbot import MarkovBot
from secret import *
import time

bot = MarkovBot()

dirname = os.path.dirname(os.path.abspath(__file__))
source = os.path.join(dirname, 'descriptions.txt')
bot.read(source)

bot.twitter_login(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
bot.twitter_tweeting_start(days=0, hours=12, minutes=00, keywords=None, prefix=None, suffix=None)
time.sleep(30)
bot.twitter_tweeting_stop()
