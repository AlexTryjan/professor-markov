import os
from markovbot import MarkovBot

bot = MarkovBot()

dirname = os.path.dirname(os.path.abspath(__file__))
source = os.path.join(dirname, 'test.txt')
bot.read(source)

text = bot.generate_text(25, seedword=['pikachu'])
print text