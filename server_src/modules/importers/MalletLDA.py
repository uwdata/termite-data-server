#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
from CommonLDA import CommonLDA

class MalletLDA( CommonLDA ):

	TOPIC_WORD_WEIGHTS = 'topic-word-weights.txt'
	DOC_TOPIC_MIXTURES = 'doc-topic-mixtures.txt'
	
	def __init__( self, app_path, model_path ):
		self.logger = logging.getLogger('termite')

		self.app_path = app_path
		self.data_path = '{}/data/lda'.format( self.app_path )
		self.model_path = model_path
		self.filenameTopicWordWeights = '{}/{}'.format( self.model_path, MalletLDA.TOPIC_WORD_WEIGHTS )
		self.filenameDocTopicMixtures = '{}/{}'.format( self.model_path, MalletLDA.DOC_TOPIC_MIXTURES )
	
	def Exists( self ):
		return os.path.exists( self.data_path )
	
	def Execute( self ):
		if not os.path.exists( self.data_path ):
			os.makedirs( self.data_path )
		self.ReadTopicWordWeights()
		self.ReadDocTopicMixtures()
		self.SaveToDisk()
		self.TransposeMatrices()
		self.ComputeTopicCooccurrenceAndCovariance()
	
	def ReadTopicWordWeights( self ):
		self.logger.info( 'Reading topic-term matrix: %s', self.filenameTopicWordWeights )
		self.termSet = set()
		self.topicSet = set()
		self.termFreqs = {}
		self.topicFreqs = []
		self.termsAndTopics = {}
		with open( self.filenameTopicWordWeights, 'r' ) as f:
			for line in f:
				line = line.rstrip('\n').decode('utf-8')
				topic, term, value = line.split('\t')
				topic = int(topic)
				value = float(value)
				if topic not in self.topicSet:
					self.topicSet.add( topic )
					self.topicFreqs.append( 0.0 )
				if term not in self.termSet:
					self.termSet.add( term )
					self.termFreqs[ term ] = 0.0
					self.termsAndTopics[ term ] = []
				self.termsAndTopics[ term ].append( value )
				self.topicFreqs[ topic ] += value
				self.termFreqs[ term ] += value
		self.topicCount = len(self.topicSet)
		self.termCount = len(self.termSet)
	
	def ReadDocTopicMixtures( self ):
		self.logger.info( 'Reading doc-topic matrix: %s', self.filenameDocTopicMixtures )
		self.docSet = set()
		self.docsAndTopics = {}
		header = None
		with open( self.filenameDocTopicMixtures, 'r' ) as f:
			for line in f:
				line = line.rstrip('\n').decode('utf-8')
				if header is None:
					assert line == "#doc name topic proportion ..."
					header = line
				else:
					fields = line.split( '\t' )
					docIndex = int(fields[0])
					docID = fields[1]
					topicKeys = [ int(key) for n, key in enumerate(fields[2:]) if n % 2 == 0 and key != '' ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n % 2 == 1 and value != '' ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if docID not in self.docSet:
							self.docSet.add( docID )
							self.docsAndTopics[ docID ] = [ 0.0 ] * self.topicCount
						self.docsAndTopics[ docID ][ topic ] = value
		self.docCount = len(self.docSet)

	def SaveToDisk( self ):
		docList = sorted( self.docSet )
		termList = sorted( self.termSet, key = lambda x : -self.termFreqs[x] )
		topicList = sorted( self.topicSet )
		
		docIndex = []
		termIndex = []
		topicIndex = []
		for term in termList:
			termIndex.append({
				'text' : term,
				'freq' : self.termFreqs[ term ]
			})
		for docID in docList:
			docIndex.append({
				'docID' : docID,
			})
		for topic in topicList:
			topicIndex.append({
				'index' : topic,
				'freq' : self.topicFreqs[ topic ]
			})
		
		self.logger.info( 'Writing data to disk: %s', self.data_path )
		filename = '{}/doc-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )			
		filename = '{}/term-topic-matrix.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.termsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.docsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
