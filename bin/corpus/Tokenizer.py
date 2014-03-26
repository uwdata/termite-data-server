#!/usr/bin/env python

import re

class Tokenizer(object):
	WHITESPACES = re.compile(r'\W+')
	
	def __init__(self, minChars=3, stopwords=[]):
		self.minChars = minChars
		self.stopwords = frozenset(stopwords)
		
	def Tokenize(self, content):
		"""
		Tokenize, lowercase, remove stopwords etc. from a unicode string.
		"""
		tokens = Tokenizer.WHITESPACES.split(content)
		tokens = [ token.lower() for token in tokens if len(token) >= self.minChars and token.isalpha() ]
		tokens = [ token for token in tokens if token not in self.stopwords ]
		return tokens
