#!/usr/bin/env python

import subprocess
import time
from datetime import datetime
from threading import Thread
from Queue import Queue, Empty
from CorpusReader import CorpusReader

class SentenceReader(object):
	SENTENCE_SPLITTER = 'utils/corenlp/StreamingSentenceSplitter.jar'
	
	def __init__(self, path, minChars=3, stopwords=[]):
		self.reader = CorpusReader(path, minChars, stopwords)
		self.process = subprocess.Popen( [ "java", "-jar", SentenceReader.SENTENCE_SPLITTER ], stdout = subprocess.PIPE, stdin = subprocess.PIPE )
		self.queue = Queue()
		self.thread = Thread( target = self.SplitSentencesWorker, args = ( self.queue, self.process ) )
		self.thread.daemon = True
		self.thread.start()

	def Load(self):
		"""
		Load a corpus using CorpusReader, and split by sentences.
		"""
		numSentences = 0
		for docID, docContent, docTokens in self.reader.Load():
			self.SplitSentencesBefore(docID, docContent)
			while not self.queue.empty():
				numSentences += 1
				yield self.SplitSentencesAfter()
		
		self.process.stdin.flush()
		startTime = datetime.now()
		while self.process.poll() is None:
			while not self.queue.empty():
				startTime = datetime.now()
				numSentences += 1
				yield self.SplitSentencesAfter()
			endTime = datetime.now()
			inactivity = (endTime - startTime).seconds
			if inactivity >= 2.5: # Wait for 2.5 second of pause
				break
			else:
				time.sleep( 0.25 )
		self.process.stdin.close()
		self.length = numSentences

	def SplitSentencesBefore(self, docID, docContent):
		line = u'{}\t{}\n'.format(docID, docContent).encode('utf-8')
		self.process.stdin.write(line)

	def SplitSentencesWorker( self, queue, process ):
		while process.poll() is None:
			line = process.stdout.readline()
			queue.put(line[:-1]) # Remove line break

	def SplitSentencesAfter(self):
		line = self.queue.get().decode('utf-8')
		fields = line.split('\t')
		docID = fields[0]
		docSubID = fields[1]
		docSentence = fields[2]
		docTokens = self.reader.tokenizer.Tokenize(docSentence)
		return docID, docSubID, docSentence, docTokens

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
		for docID, docSubID, docSentence, docTokens in reader.Load():
			print docID
			print docSubID
			print docSentence
			print docTokens
			print
		print "Actual/Expected = {}/{} sentences".format( reader.length, 3406 )
	if args.newsgroups:
		reader = SentenceReader('data/demo/20newsgroups/corpus', minChars=minChars, stopwords=stopwords)
		for docID, docSubID, docSentence, docTokens in reader.Load():
			print docID
			print docSubID
			print docSentence
			print docTokens
			print
		print "Actual/Expected = {}/{} sentences".format( reader.length, 449 )

if __name__ == '__main__':
	main()
