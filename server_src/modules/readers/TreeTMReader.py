#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from .LDAReader import LDAReader

class TreeTMReader(LDAReader):
	"""
	lda_db = a SQLite3 database
	modelPath = a model folder containing files corpus.voc, model.topic-words, and model.docs
	"""
	
	PROB_THRESHOLD = 0.001
	CORPUS_VOCAB_FILENAME = 'corpus.voc'
	TOPIC_WORDS_FILENAME = 'model.topic-words'
	DOC_TOPICS_FILENAME = 'model.docs'
	
	def __init__(self, lda_db, modelPath):
		super(TreeTMReader, self).__init__(lda_db)
		self.modelPath = modelPath
		self.entryPath = self.GetLatestEntry()
		self.corpusVocab = '{}/{}'.format( self.modelPath, TreeTMReader.CORPUS_VOCAB_FILENAME )
		self.entryTopicWordWeights = '{}/{}'.format( self.entryPath, TreeTMReader.TOPIC_WORDS_FILENAME )
		self.entryDocTopicMixtures = '{}/{}'.format( self.entryPath, TreeTMReader.DOC_TOPICS_FILENAME )

	def Execute(self):
		self.logger.info( 'Reading ITM topic model output...' )
		self.ReadVocabFile()
		self.ReadTopicWordWeights()
		self.ReadDocTopicMixtures()
		self.logger.info( 'Writing to database...' )
		self.SaveToDB()

	def GetLatestEntry( self ):
		entries = []
		for filename in os.listdir( self.modelPath ):
			path = '{}/{}'.format( self.modelPath, filename )
			# Keep only folders that begin with "entry-". This will prevent
			# folders like "corpus" to be the last in the list
			if os.path.isdir( path ) and filename.startswith('entry-'):
				entries.append(path)
		# This is so entry-X is listed after entry-Y, X > Y
		entries.sort()
		return entries[-1]

	def ReadVocabFile( self ):
		self.termList = []
		self.logger.debug( '    Loading vocbuary: %s', self.corpusVocab )
		with open( self.corpusVocab ) as f:
			self.termList = [ line.strip('\n').split('\t')[1] for line in f ]

	def ReadTopicWordWeights( self ):
		accumulator = {}
		self.logger.debug( '    Loading matrix: %s', self.entryTopicWordWeights )
		with open( self.entryTopicWordWeights, 'r' ) as f:
			for line in f:
				line = line.strip('\n')
				topicIndex, term, value = line.split('\t')
				topicIndex = int(topicIndex)
				value = float(value)
				if value > TreeTMReader.PROB_THRESHOLD:
					if term not in accumulator:
						accumulator[term] = {}
					if topicIndex not in accumulator[term]:
						accumulator[term][topicIndex] = 0.0
					accumulator[term][topicIndex] += value
		self.termTopicMatrix = []
		for term in accumulator:
			for topicIndex in accumulator[term]:
				value = accumulator[term][topicIndex]
				self.termTopicMatrix.append({
					'term_index' : term,
					'topic_index' : topicIndex,
					'value' : value,
					'rank' : 0
				})
		termLookup = { term : termIndex for termIndex, term in enumerate(self.termList) }
		self.termTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.termTopicMatrix):
			d['term_index'] = termLookup[d['term_index']]
			d['rank'] = index + 1

	def ReadDocTopicMixtures( self ):
		self.docList = []
		self.docTopicMatrix = []
		docSet = set()
		self.logger.debug( '    Loading matrix: %s', self.entryDocTopicMixtures )
		with open( self.entryDocTopicMixtures, 'r' ) as f:
			for index, line in enumerate(f):
				line = line.strip('\n')
				if index == 0:
					pass
#					assert line == "#doc source topic proportion ..."
				else:
					fields = line.split( ' ' )
					docIndex = int(fields[0])
					docId = fields[1]
					topicIndexes = [ int(d) for n, d in enumerate(fields[2:]) if n % 2 == 0 and d != '' ]
					values = [ float(d) for n, d in enumerate(fields[2:]) if n % 2 == 1 and d != '' ]
					for n, topicIndex in enumerate(topicIndexes):
						value = values[n]
						if value > TreeTMReader.PROB_THRESHOLD:
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
