#!/usr/bin/env python
# -*- coding: utf-8 -*-

from LDAReader import LDAReader

class MalletReader(LDAReader):
	"""
	lda_db = a SQLite3 database
	modelPath = a model folder containing files topic-word-weights.txt and doc-topic-mixtures.txt
	"""
	
	FREQ_THRESHOLD = 1
	PROB_THRESHOLD = 0.001
	TOPIC_WORD_WEIGHTS_FILENAME = 'topic-word-weights.txt'
	DOC_TOPIC_MIXTURES_FILENAME = 'doc-topic-mixtures.txt'
	
	def __init__(self, lda_db, modelPath):
		super(MalletReader, self).__init__(lda_db)
		self.modelPath = modelPath
		self.modelTopicWordWeights = '{}/{}'.format( self.modelPath, MalletReader.TOPIC_WORD_WEIGHTS_FILENAME )
		self.modelDocTopicMixtures = '{}/{}'.format( self.modelPath, MalletReader.DOC_TOPIC_MIXTURES_FILENAME )
	
	def Execute(self):
		self.logger.info( 'Reading MALLET LDA output...' )
		self.ReadTopicWordWeights()
		self.ReadDocTopicMixtures()
		self.logger.info( 'Writing to database...' )
		self.SaveToDB()
	
	def ReadTopicWordWeights( self ):
		self.termList = []
		self.termTopicMatrix = []
		termSet = set()
		self.logger.debug( '    Loading matrix: %s', self.modelTopicWordWeights )
		with open(self.modelTopicWordWeights, 'r') as f:
			for line in f:
				line = line.rstrip('\n').decode('utf-8')
				topicIndex, term, value = line.split('\t')
				topicIndex = int(topicIndex)
				value = float(value)
				if value > MalletReader.FREQ_THRESHOLD:
					self.termTopicMatrix.append({
						'term_index' : term,
						'topic_index' : topicIndex,
						'value' : value,
						'rank' : 0
					})
				if term not in termSet:
					termSet.add(term)
					self.termList.append(term)
		termLookup = { term : termIndex for termIndex, term in enumerate(self.termList) }
		self.termTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.termTopicMatrix):
			d['term_index'] = termLookup[d['term_index']]
			d['rank'] = index + 1

	def ReadDocTopicMixtures( self ):
		self.docList = []
		self.docTopicMatrix = []
		docSet = set()
		self.logger.debug( '    Loading matrix: %s', self.modelDocTopicMixtures )
		with open(self.modelDocTopicMixtures, 'r') as f:
			for index, line in enumerate(f):
				line = line.rstrip('\n').decode('utf-8')
				if index == 0:
					assert line == "#doc name topic proportion ..."
				else:
					fields = line.split( '\t' )
					docIndex = int(fields[0])
					docId = fields[1]
					topicIndexes = [ int(d) for n, d in enumerate(fields[2:]) if n % 2 == 0 and d != '' ]
					values = [ float(d) for n, d in enumerate(fields[2:]) if n % 2 == 1 and d != '' ]
					for n, topicIndex in enumerate(topicIndexes):
						value = values[n]
						if value > MalletReader.PROB_THRESHOLD:
							self.docTopicMatrix.append({
								'doc_index' : docId,
								'topic_index' : topicIndex,
								'value' : value,
								'rank' : 0
							})
						if docId not in docSet:
							docSet.add(docId)
							self.docList.append(docId)
		docLookup = { docId : docIndex for docIndex, docId in enumerate(self.docList) }
		self.docTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.docTopicMatrix):
			d['doc_index'] = docLookup[d['doc_index']]
			d['rank'] = index + 1
