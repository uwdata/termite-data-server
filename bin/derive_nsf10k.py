#!/usr/bin/env python

import json
import os
from corpus.Tokenizer import Tokenizer

INPUT_CORPUS = 'data/demo/nsf146k/corpus/nsf146k-src.txt'
OUTPUT_PATH = 'data/demo/nsf10k/corpus'
OUTPUT_CORPUS = '{}/nsf10k-src.txt'.format( OUTPUT_PATH )
tokenizer = Tokenizer( stopwords = 'tools/mallet/stoplists/en.txt' )

def ReadAll( searchTerms ):
	corpus = {}
	docIDs = set()
	with open( INPUT_CORPUS, 'r' ) as f:
		for index, line in enumerate(f):
			line = line[:-1]
			docID, content = line.split('\t')
			tokens = frozenset( tokenizer.Tokenize(content) )
			matches = set()
			for searchTerm in searchTerms:
				if searchTerm in tokens:
					matches.add(searchTerm)
			if len(matches) >= 3:
				for match in matches:
					if match not in corpus:
						corpus[match] = []
					corpus[match].append(docID)
					docIDs.add(docID)
			if index % 5000 == 0:
				print 'reading {} documents...'.format( index )
	return corpus, docIDs

def WriteAll( docIDs ):
	if not os.path.exists( OUTPUT_PATH ):
		os.makedirs( OUTPUT_PATH )
	with open( INPUT_CORPUS, 'r' ) as f:
		with open( OUTPUT_CORPUS, 'w' ) as g:
			for index, line in enumerate(f):
				line = line[:-1]
				docID, content = line.split('\t')
				if docID in docIDs:
					g.write( '{}\t{}\n'.format( docID, content ) )
				if index % 5000 == 0:
					print 'writing {} documents...'.format( index )

corpus, docIDs = ReadAll( [ "visualization", "visualizations", "user", "users", "evaluation", "evaluations", "hci", "cognitive", "cognition", "psychology", "design", "designs", "human", "humans", "information", "data", "retrieve", "retrieval", "classify", "classification", "categorize", "category", "categories" ] )

# print json.dumps( { key : len(docs) for key, docs in corpus.iteritems() }, indent = 2, sort_keys = True )
# print len(docIDs)

WriteAll( docIDs )