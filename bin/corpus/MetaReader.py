#!/usr/bin/env python

import re
import os
import glob

class MetaReader(object):
	WHITESPACES = re.compile(r'\W+')

	def __init__(self, path, minChars=3, stopwords=[], fromCorpus=False):
		self.path = path
		self.minChars = minChars
		self.stopwords = frozenset(stopwords)
		self.header = None
		self.fromCorpus = fromCorpus
	
	def Load(self):
		"""
		Load a tab-delimited file with a header line containing at least two fields 'DocID' and 'DocContent'.
		"""
		numDocs = 0
		self.header = None
		if self.fromCorpus:
			self.header = [
				{'index':0, 'name':'DocID', 'type':'str'},
				{'index':1, 'name':'DocContent', 'type':'str'}
			]
		with open(self.path) as f:
			for line in f:
				if self.header is None:
					fields = line[:-1].decode('utf-8', 'ignore').split('\t')
					self.header = [ {'index':n, 'name':field, 'type':'str'} for n, field in enumerate(fields) ]
				else:
					values = line[:-1].decode('utf-8', 'ignore').split('\t')
					content = { self.header[i]['name'] : value for i, value in enumerate(values) }
					docID = content['DocID']
					docContent = content['DocContent']
					docTokens = MetaReader.WHITESPACES.split(docContent)
					content['DocTokens'] = self.Preprocess(docTokens)
					yield docID, content
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
	parser = argparse.ArgumentParser( description = 'Test MetaReader on the infovis dataset' )
	parser.add_argument( '--min-chars'   , dest = 'minChars'  , action = 'store', type = int, default = 3   , help = 'Minimum number of characters per token' )
	parser.add_argument( '--stopwords'   , dest = 'stopwords' , action = 'store', type = str, default = None, help = 'A file containing a list of stopwords, one per line' )
	args = parser.parse_args()
	
	minChars = args.minChars
	stopwords = []
	if args.stopwords is not None:
		with open(args.stopwords) as f:
			stopwords = f.read().decode('utf-8', 'ignore').splitlines()
	reader = MetaReader('data/demo/infovis/corpus/infovis-papers-meta.txt')
	for docID, docMeta in reader.Load():
		print docID
		print docMeta
		print
	print reader.header

if __name__ == '__main__':
	main()
