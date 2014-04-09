#!/usr/bin/env python

from CorpusReader import CorpusReader
from Tokenizer import Tokenizer

class MetaReader(object):

	def __init__(self, path, minChars=3, stopwords=[], fromCorpus=False):
		self.fromCorpus = fromCorpus
		if self.fromCorpus:
			self.reader = CorpusReader(path, minChars, stopwords)
		else:
			self.reader = None
			self.path = path
			self.tokenizer = Tokenizer(minChars, stopwords)
		self.header = None
	
	def ParseInt( self, s ):
		try:
			int( s )
			return True
		except ValueError:
			return False
	
	def ParseFloat( self, s ):
		try:
			float( s )
			return True
		except ValueError:
			return False

	def Load(self):
		"""
		Load a tab-delimited file with a header line containing at least two fields 'DocID' and 'DocContent'.
		Alternatively, load a corpus file/folder using CorpusReader.
		"""
		numDocs = 0
		if self.fromCorpus:
			self.header = [
				{'index':0, 'name':'DocID', 'type':'string'},
				{'index':1, 'name':'DocContent', 'type':'string'},
				{'index':2, 'name':'DocTokens', 'type':'string'}
			]
			for docID, docContent, docTokens in self.reader.Load():
				content = {
					'DocID' : docID,
					'DocContent' : docContent,
					'DocTokens' : ' '.join(docTokens)
				}
				numDocs += 1
				yield docID, content
		else:
			self.header = None
			self.isInteger = None
			self.isFloat = None
			with open(self.path) as f:
				for line in f:
					if self.header is None:
						fields = line[:-1].decode('utf-8', 'ignore').split('\t')
						self.header = [ {'index':n, 'name':field, 'type':'string'} for n, field in enumerate(fields) ]
						self.header.append( {'index':len(self.header), 'name':'DocTokens', 'type':'string'} )
						self.isInteger = [ True for _ in range(len(self.header)) ]
						self.isFloat = [ True for _ in range(len(self.header)) ]
					else:
						values = line[:-1].decode('utf-8', 'ignore').split('\t')
						content = { self.header[i]['name'] : value for i, value in enumerate(values) }
						docID = content['DocID']
						docContent = content['DocContent']
						docTokens = self.tokenizer.Tokenize(docContent)
						content['DocTokens'] = ' '.join(docTokens)
						for i, header in enumerate(self.header):
							if self.isInteger[i]:
								self.isInteger[i] = self.isInteger[i] and self.ParseInt( content[header['name']] )
							if not self.isInteger[i] and self.isFloat[i]:
								self.isFloat[i] = self.isFloat[i] and self.ParseFloat( content[header['name']] )
						numDocs += 1
						yield docID, content
			for i, _ in enumerate(self.header):
				if self.isInteger[i]:
					self.header[i]['type'] = 'integer'
				elif self.isFloat[i]:
					self.header[i]['type'] = 'real'
		self.length = numDocs

def main():
	import argparse
	parser = argparse.ArgumentParser( description = 'Test MetaReader on the infovis dataset' )
	parser.add_argument( '--min-chars'   , dest = 'minChars'  , action = 'store'      , type = int  , default = 3     , help = 'Minimum number of characters per token' )
	parser.add_argument( '--stopwords'   , dest = 'stopwords' , action = 'store'      , type = str  , default = None  , help = 'Stopwords, one per line as a file' )
	parser.add_argument( '--from-corpus' , dest = 'fromCorpus', action = 'store_const', const = True, default = False , help = 'Load from a corpus file instead' )
	args = parser.parse_args()
	
	minChars = args.minChars
	stopwords = []
	if args.stopwords is not None:
		with open(args.stopwords) as f:
			stopwords = f.read().decode('utf-8', 'ignore').splitlines()
	if args.fromCorpus:
		reader = MetaReader('data/demo/infovis/corpus/infovis-papers.txt', fromCorpus=True)
	else:
		reader = MetaReader('data/demo/infovis/corpus/infovis-papers-meta.txt')
	for docID, docMeta in reader.Load():
		print docID
		print docMeta
		print
	print reader.header
	print
	print "Actual/Expected = {}/{} documents".format( reader.length, 449 )

if __name__ == '__main__':
	main()
