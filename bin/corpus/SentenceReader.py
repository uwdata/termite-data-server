#!/usr/bin/env python

import re
import os
import glob
import subprocess
import time
from threading import Thread
from Queue import Queue, Empty
from datetime import datetime

class SentenceReader(object):
	WHITESPACES = re.compile(r'\W+')
	LINEBREAKS = re.compile(r'[\t\n\x0B\f\r]+')
	SENTENCE_SPLITTER = 'utils/corenlp/StreamingSentenceSplitter.jar'
	
	def __init__(self, path, minChars=3, stopwords=[]):
		self.path = path
		self.minChars = minChars
		self.stopwords = frozenset(stopwords)
		self.process = subprocess.Popen( [ "java", "-jar", SentenceReader.SENTENCE_SPLITTER ], stdout = subprocess.PIPE, stdin = subprocess.PIPE )
		self.queue = Queue();
		self.thread = Thread( target = self.SplitSentencesWorker, args = ( self.queue, self.process ) )
		self.thread.daemon = True
		self.thread.start()

	def Load(self):
		"""
		Load a corpus that is either:
		(1) a single file with one document per line or
		(2) a folder where each document is stored as a file (up to 2 levels of subfolders).
		"""
		self.numSentences = 0
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
						docContent = SentenceReader.LINEBREAKS.sub(' ', f.read().decode('utf-8', 'ignore')).strip()
						self.SplitSentencesBefore(docID, docContent)
						while not self.queue.empty():
							yield self.SplitSentencesAfter()
		else:
			with open(self.path) as f:
				for line in f:
					docID, docContent = line[:-1].decode('utf-8', 'ignore').split('\t')
					self.SplitSentencesBefore(docID, docContent)
					while not self.queue.empty():
						yield self.SplitSentencesAfter()
		
		startTime = datetime.now()
		while self.process.poll() is None:
			while not self.queue.empty():
				startTime = datetime.now()
				yield self.SplitSentencesAfter()
			endTime = datetime.now()
			inactivity = (endTime - startTime).seconds
			if inactivity >= 1.0: # Wait for 1.0 second of pause
				break
			else:
				time.sleep( 0.25 )
		self.process.stdin.close()
		self.length = self.numSentences

	def SplitSentencesBefore(self, docID, docContent):
		line = u'{}\t{}\n'.format(docID, docContent).encode('utf-8')
		self.process.stdin.write(line)
		self.process.stdin.flush()

	def SplitSentencesWorker( self, queue, process ):
		while process.poll() is None:
			line = process.stdout.readline()
			queue.put(line)

	def SplitSentencesAfter(self):
		line = self.queue.get().decode('utf-8')
		fields = line.split('\t')
		docID = fields[0]
		docSubID = fields[1]
		docSentence = fields[2]
		self.numSentences += 1
		docTokens = SentenceReader.WHITESPACES.split(docSentence)
		return docID, docSubID, self.Preprocess(docTokens)
	
	def Preprocess(self, tokens):
		"""
		Lowercase, remove stopwords etc. from a list of unicode strings.
		"""
		result = [ token.lower() for token in tokens if len(token) >= self.minChars and token.isalpha() ]
		return [ token for token in result if token not in self.stopwords ]

def main():
	import argparse
	parser = argparse.ArgumentParser( description = 'Test SentenceReader on the infovis and/or 20newsgroups dataset(s)' )
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
		reader = SentenceReader('data/demo/infovis/corpus/infovis-papers.txt', minChars=minChars, stopwords=stopwords)
		for docID, i, docContent in reader.Load():
			print docID
			print i
			print docContent
			print
		print reader.length
	if args.newsgroups:
		reader = SentenceReader('data/demo/20newsgroups/corpus', minChars=minChars, stopwords=stopwords)
		for docID, i, docContent in reader.Load():
			print docID
			print i
			print docContent
			print
		print reader.length

if __name__ == '__main__':
	main()
