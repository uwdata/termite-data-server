#!/usr/bin/env python

import re
import os
import glob

class CorpusReader(object):
	WHITESPACES = re.compile(r'\W+')
	LINEBREAKS = re.compile(r'[\t\n\x0B\f\r]+')
	
	def __init__(self, path, minChars=3, stopwords=[]):
		self.path = path
		self.minChars = minChars
		self.stopwords = frozenset(stopwords)
	
	def Load(self):
		"""
		Load a corpus that is either:
		(1) a single file with one document per line or
		(2) a folder where each document is stored as a file (up to 2 levels of subfolders).
		"""
		numDocs = 0
		if os.path.isdir(self.path):
			# Read two levels of files
			filenames = glob.glob('{}/*'.format(self.path))
			for filename in filenames:
				if os.path.isdir(filename):
					filenames += glob.glob('{}/*'.format(filename))
			for filename in filenames:
				if not os.path.isdir(filename):
					with open(filename) as f:
						docID = filename
						docContent = CorpusReader.LINEBREAKS.sub(' ', f.read().decode('utf-8', 'ignore')).strip()
						docTokens = CorpusReader.WHITESPACES.split(docContent)
						yield docID, self.Preprocess(docTokens)
						numDocs += 1
		else:
			with open(self.path) as f:
				for line in f:
					docID, docContent = line[:-1].decode('utf-8', 'ignore').split('\t')
					docTokens = CorpusReader.WHITESPACES.split(docContent)
					yield docID, self.Preprocess(docTokens)
					numDocs += 1
		self.length = numDocs
	
	def Preprocess(self, tokens):
		"""
		Lowercase, remove stopwords etc. from a list of unicode strings.
		"""
		result = [ token.lower() for token in tokens if len(token) >= self.minChars and token.isalpha() ]
		return [ token for token in result if token not in self.stopwords ]

def main():
	import argparse
	parser = argparse.ArgumentParser( description = 'Test CorpusReader on the infovis and/or 20newsgroups dataset(s)' )
	parser.add_argument( '--infovis'     , dest = 'infovis'   , action = 'store_const', const = True, default = False, help = 'Load the infovis dataset' )
	parser.add_argument( '--20newsgroups', dest = 'newsgroups', action = 'store_const', const = True, default = False, help = 'Load the 20newsgroupds dataset' )
	parser.add_argument( '--min-chars'   , dest = 'minChars'  , action = 'store'      , type = int  , default = 3    , help = 'Minimum number of characters per token' )
	parser.add_argument( '--stopwords'   , dest = 'stopwords' , action = 'store'      , type = str  , default = None , help = 'A file containing a list of stopwords, one per line' )
	args = parser.parse_args()
	
	minChars = args.minChars
	stopwords = []
	if args.stopwords is not None:
		with open(args.stopwords) as f:
			stopwords = f.read().decode('utf-8', 'ignore').splitlines()
	if args.infovis:
		reader = CorpusReader('data/demo/infovis/corpus/infovis-papers.txt', minChars=minChars, stopwords=stopwords)
		for docID, docContent in reader.Load():
			print docID
			print docContent
			print
		print reader.length
	if args.newsgroups:
		reader = CorpusReader('data/demo/20newsgroups/corpus', minChars=minChars, stopwords=stopwords)
		for docID, docContent in reader.Load():
			print docID
			print docContent
			print
		print reader.length

if __name__ == '__main__':
	main()
