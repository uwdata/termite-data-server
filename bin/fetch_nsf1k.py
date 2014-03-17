#!/usr/bin/env python

import json
import os

INPUT_CORPUS = 'data/demo/nsf127992/corpus/nsf127992.txt'
OUTPUT_PATH = 'data/demo/nsf1k/corpus'
OUTPUT_CORPUS = '{}/nsf1k.txt'.format( OUTPUT_PATH )

def ReadAll( searchTerms ):
	corpus = {}
	docIDs = set()
	with open( INPUT_CORPUS, 'r' ) as f:
		for index, line in enumerate(f):
			line = line[:-1]
			docID, content = line.split('\t')
			tokens = frozenset(content.split(' '))
			matches = set()
			for searchTerm in searchTerms:
				if searchTerm in tokens:
					matches.add(searchTerm)
			if len(matches) >= 5:
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