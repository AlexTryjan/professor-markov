# -*- coding: utf-8 -*-
# This file is part of markovbot, created by Edwin Dalmaijer
# GitHub: https://github.com/esdalmaijer/markovbot
#
# Markovbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Markovbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with markovbot.  If not, see <http://www.gnu.org/licenses/>.


# native imports
import os
import sys
import copy
import time
import pickle
import random
from threading import Thread, Lock
from multiprocessing import Queue


class MarkovBot():
	
	"""Class to generate text with a Markov chain
	"""
	
	def __init__(self):
		
		"""Initialises the bot.
		"""
		
		# # # # #
		# DATA

		# Create an empty dict for the data
		self.data = {u'default':{}}

		# Prepare the self-examination Thread (periodically checks whether
		# all Threads are still alive, and revives any dead ones.)
		self._selfexaminationthreadlives = True
		self._selfexaminationthread = Thread(target=self._self_examination)
		self._selfexaminationthread.daemon = True
		self._selfexaminationthread.name = u'selfexaminer'
		
		# Start all Threads.
		self._selfexaminationthread.start()
			

	def clear_data(self, database=None):
		
		"""Clears the current internal data. NOTE: This does not remove
		existing pickled data!
		
		Keyword Arguments
		
		database		-	A string that indicates the name of the
						specific database that you want to clear,
						or None to clear all data. (default = None)
		"""
		
		# Overwrite data
		if database == None:
			self.data = {'default':{}}
		else:
			try:
				self.data.pop(database)
			except KeyError:
				self._error(u'clear_data', u"There was no database named '%s'" % (database))


	def generate_text(self, maxlength, seedword=None, database=u'default',
		verbose=False, maxtries=100):
		
		"""Generates random text based on the provided database.
		
		Arguments
		
		maxlength		-	An integer value indicating the amount of words
						that can maximally be produced. The actual
						number is determined by where interpunction
						occurred. Text will be cut off at a comma,
						full stop, and exclamation or question marks.
		
		Keyword Arguments
		
		seedword		-	A string that indicates what word should be in
						the sentence. If None is passed, or if the word
						is not in the database, a random word will be
						chosen. This value can also be a list of words,
						in which case the list will be processed
						one-by-one until a word is found that is in the
						database.
		
		database		-	A string that indicates the name of the
						specific database that you want to use to
						generate the text, or u'default' to use the
						default database. (default = 'default')

		verbose		-	Boolean that indicates whether this function
						should bother you with excessibe and unnecessary
						messages whenever it can't immeadiately produce
						a text (it will still raise an Exception after
						maxtries attempts).
		
		maxtries		-	Integer indicating how many attempts the function
						is allowed to construct some text (sometimes
						this fails, and I couldn't be bothered to do
						elaborate debugging)
		
		Returns
		
		sentence		-	A string that starts with a capital, and ends
						with a full stop.
		"""
		
		# Raise an Exception when no data exists
		if self.data[database] == {}:
			self._error(u'generate_text', u"No data is available yet in database '%s'. Did you read any data yet?" % (database))
		
		# Sometimes, for mysterious reasons, a word duo does not appear as a
		# key in the database. This results in a KeyError, which is highly
		# annoying. Because I couldn't quite find the bug that causes this
		# after a whopping five minutes of looking for it, I decided to go
		# with the lazy approach of using a try and except statements. Sorry.
		error = True
		attempts = 0
		
		# Make a single keyword into a list of them
		if type(seedword) in [str,unicode]:
			seedword = [seedword]

		# Run until a proper sentence is produced
		while error:
			
			try:
				# Get all word duos in the database
				keys = self.data[database].keys()
				# Shuffle the word duos, so that not the same is
				# found every time
				random.shuffle(keys)
				
				# Choose a random seed to fall back on when seedword does
				# not occur in the keys, or if seedword==None
				seed = random.randint(0, len(keys))
				w1, w2 = keys[seed]
				
				# Try to find a word duo that contains the seed word
				if seedword != None:
					# Loop through all potential seed words
					while len(seedword) > 0:
						# Loop through all keys (these are (w1,w2)
						# tuples of words that occurred together in the
						# text used to generate the database
						for i in xrange(len(keys)):
							# If the seedword is only one word, check
							# if it is part of the key (a word duo)
							# If the seedword is a combination of words,
							# check if they are the same as the key
							if seedword[0] in keys[i] or \
								(tuple(seedword[0].split(u' ')) == \
								keys[i]):
								# Choose the words
								w1, w2 = keys[i]
								# Get rid of the seedwords
								seedword = []
								break
						# Get rid of the first keyword, if it was not
						# found in the word duos
						if len(seedword) > 0:
							seedword.pop(0)
				
				# Empty list to contain the generated words
				words = []
				
				# Loop to get as many words as requested
				for i in xrange(maxlength):
					# Add the current first word
					words.append(w1)
					# Generare a new first and second word, based on the
					# database. Each key is a (w1,w2 tuple that points to
					# a list of words that can follow the (w1, w2) word
					# combination in the studied text. A random word from
					# this list is selected. Note: words can occur more
					# than once in this list, thus more likely word
					# combinations are more likely to be selected here.
					w1, w2 = w2, random.choice(self.data[database][(w1, w2)])
				
				# Add the final word to the generated words
				words.append(w2)
				
				# Capitalise the first word, capitalise all single 'i's,
				# and attempt to capitalise letters that occur after a
				# full stop.
				for i in xrange(0, len(words)):
					if (i == 0) or (u'.' in words[i-1]) or \
						(words[i] == u'i'):
						words[i] = words[i].capitalize()
				
				# Find the last acceptable interpunction by looping
				# through all generated words, last-to-first, and
				# checking which is the last word that contains
				# relevant interpunction.
				ei = 0
				for i in xrange(len(words)-1, 0, -1):
					# Check whether the current word ends with
					# relevant interpunction. If it does, use the
					# current as the last word. If the interpunction
					# is not appropriate for ending a sentence with,
					# change it to a full stop.
					if words[i][-1] in [u'.', u'!', u'?']:
						ei = i+1
					elif words[i][-1] in [u',', u';', u':']:
						ei = i+1
						words[i][-1] = u'.'
					# Break if we found a word with interpunction.
					if ei > 0:
						break
				# Cut back to the last word with stop-able interpunction
				words = words[:ei]

				# Combine the words into one big sentence
				sentence = u' '.join(words)

				if sentence != u'':
					error = False
				
			# If the above code fails
			except:
				# Count one more failed attempt
				attempts += 1
				# Report the error to the console
				if verbose:
					self._message(u'generate_text', u"Ran into a bit of an error while generating text. Will make %d more attempts" % (maxtries-attempts))
				# If too many attempts were made, raise an error to stop
				# making any further attempts
				if attempts >= maxtries:
					self._error(u'generate_text', u"Made %d attempts to generate text, but all failed. " % (attempts))

		return sentence
		
	
	def read(self, filename, database=u'default', overwrite=False):
		
		"""Reads a text, and adds its stats to the internal data. Use the
		mode keyword to overwrite the existing data, or to add the new
		reading material to the existing data. NOTE: Only text files can be
		read! (This includes .txt files, but can also be .py or other script
		files if you want to be funny and create an auto-programmer.)
		
		Arguments
		
		filename		-	String that indicates the path to a .txt file
						that should be read by the bot.
		
		Keyword Arguments
		
		database		-	A string that indicates the name of the
						specific database that you want to add the
						file's data to, or u'default' to add to the
						default database. (default = 'default')

		overwrite		-	Boolean that indicates whether the existing data
						should be overwritten (True) or not (False). The
						default value is False.
		"""
		
		# Clear the current data if required
		if overwrite:
			self.clear_data(database=database)
		
		# Check whether the file exists
		if not self._check_file(filename):
			self._error(u'read', u"File does not exist: '%s'" % (filename))
		
		# Read the words from the file as one big string
		with open(filename, u'r') as f:
			# Read the contents of the file
			contents = f.read()
		# Unicodify the contents
		contents = contents.decode(u'utf-8')
		
		# Split the words into a list
		words = contents.split()
		
		# Create a new database if this is required.
		if not database in self.data.keys():
			self._message(u'read', \
			u"Creating new database '%s'" % (database))
			self.data[database] = {}
		
		# Add the words and their likely following word to the database
		for w1, w2, w3 in self._triples(words):
			# Only use actual words and words with minimal interpunction
			if self._isalphapunct(w1) and self._isalphapunct(w2) and \
				self._isalphapunct(w3):
				# The key is a duo of words
				key = (w1, w2)
				# Check if the key is already part of the database dict
				if key in self.data[database]:
					# If the key is already in the database dict,
					# add the third word to the list
					self.data[database][key].append(w3)
				else:
					# If the key is not in the database dict yet, first
					# make a new list for it, and then add the new word
					self.data[database][key] = [w3]


	def _check_file(self, filename, allowedext=None):
		
		"""Checks whether a file exists, and has a certain extension.
		
		Arguments
		
		filename		-	String that indicates the path to a .txt file
						that should be read by the bot.
		
		Keyword Arguments
		
		allowedext	-	List of allowed extensions, or None to allow all
						extensions. Default value is None.
		
		Returns
		
		ok			-	Boolean that indicates whether the file exists,
						andhas an allowed extension (True), or does not
						(False)
		"""
		
		# Check whether the file exists
		ok = os.path.isfile(filename)
		
		# Check whether the extension is allowed
		if allowedext != None:
			name, ext = os.path.splitext(filename)
			if ext not in allowedext:
				ok = False
		
		return ok
	
	
	def _cpr(self):
		
		"""Checks on the Threads that are supposed to be running, and
		revives them when they are dead.
		"""
		
		# Check on the auto-reply Thread.

		# Check on the self-examination Thread.
		if self._selfexaminationthreadlives:
			# Check if the Thread is still alive.
			if not self._selfexaminationthread.is_alive():
				# Report on the reviving.
				self._message(u'_cpr', u'Ironically, _selfexaminationthread died; trying to revive!')
				# Restart the Thread.
				self._selfexaminationthread = Thread(self._self_examination)
				self._selfexaminationthread.daemon = True
				self._selfexaminationthread.name = u'selfexaminer'
				self._selfexaminationthread.start()
				# Report on success!
				self._message(u'_cpr', u'Succesfully restarted _selfexaminationthread!')

	def _error(self, methodname, msg):
		
		"""Raises an Exception on behalf of the method involved.
		
		Arguments
		
		methodname	-	String indicating the name of the method that is
						throwing the error.
		
		message		-	String with the error message.
		"""
		
		raise Exception(u"ERROR in Markovbot.%s: %s" % (methodname, msg))


	def _isalphapunct(self, string):
		
		"""Returns True if all characters in the passed string are
		alphabetic or interpunction, and there is at least one character in
		the string.
		
		Allowed interpunction is . , ; : ' " ! ?
		
		Arguments
		
		string	-		String that needs to be checked.
		
		Returns
		
		ok			-	Boolean that indicates whether the string
						contains only letters and allowed interpunction
						(True) or not (False).
		"""
		
		if string.replace(u'.',u'').replace(u',',u'').replace(u';',u''). \
			replace(u':',u'').replace(u'!',u'').replace(u'?',u''). \
			replace(u"'",u'').isalpha():
			return True
		else:
			return False
	
	
	def _message(self, methodname, msg):
		
		"""Prints a message on behalf of the method involved. Friendly
		verion of self._error
		
		Arguments
		
		methodname	-	String indicating the name of the method that is
						throwing the error.
		
		message		-	String with the error message.
		"""
		
		print(u"MSG from Markovbot.%s: %s" % (methodname, msg))


	def _self_examination(self):
		
		"""This function runs in the self-examination Thread, and
		continuously checks whether the other Threads are still alive.
		"""
		
		# Run until the Boolean is set to False.
		while self._selfexaminationthreadlives:
			
			# Sleep for a bit to avoid wasting resources.
			time.sleep(5)
			
			# Check if the Threads are alive, and revive if necessary.
			self._cpr()


	def _triples(self, words):
	
		"""Generate triplets from the word list
		This is inspired by Shabda Raaj's blog on Markov text generation:
		http://agiliq.com/blog/2009/06/generating-pseudo-random-text-with-markov-chains-u/
		
		Moves over the words, and returns three consecutive words at a time.
		On each call, the function moves one word to the right. For example,
		"What a lovely day" would result in (What, a, lovely) on the first
		call, and in (a, lovely, day) on the next call.
		
		Arguments
		
		words		-	List of strings.
		
		Yields
		
		(w1, w2, w3)	-	Tuple of three consecutive words
		"""
		
		# We can only do this trick if there are more than three words left
		if len(words) < 3:
			return
		
		for i in range(len(words) - 2):
			yield (words[i], words[i+1], words[i+2])
