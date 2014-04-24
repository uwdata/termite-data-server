#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class MalletReader():
	"""
	modelPath = a model folder containing files topic-word-weights.txt and doc-topic-mixtures.txt
	LDA_DB = a SQLite3 database
	"""
	
	THRESHOLD = 0.01
	TOPIC_WORD_WEIGHTS_FILENAME = 'topic-word-weights.txt'
	DOC_TOPIC_MIXTURES_FILENAME = 'doc-topic-mixtures.txt'
	
	def __init__( self, modelPath, LDA_DB ):
		self.logger = logging.getLogger('termite')
		self.modelPath = modelPath
		self.modelTopicWordWeights = '{}/{}'.format( self.modelPath, MalletReader.TOPIC_WORD_WEIGHTS_FILENAME )
		self.modelDocTopicMixtures = '{}/{}'.format( self.modelPath, MalletReader.DOC_TOPIC_MIXTURES_FILENAME )
		self.ldaDB = LDA_DB
	
	def Execute(self):
		self.ReadTopicWordWeights()
		self.ReadDocTopicMixtures()
		self.SaveToDB()
	
	def ReadTopicWordWeights( self ):
		self.logger.info( 'Reading topic-term matrix: %s', self.modelTopicWordWeights )
		self.termSet = set()
		self.topicSet = set()
		self.termFreqs = {}
		self.topicFreqs = []
		self.termsAndTopics = {}
		with open( self.modelTopicWordWeights, 'r' ) as f:
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
				self.topicFreqs[ topic ] += value
				self.termFreqs[ term ] += value
				self.termsAndTopics[ term ].append( value )
		
		self.topTerms = []
		for topic in self.topicSet:
			topTerms = sorted( self.termSet, key = lambda x : -self.termsAndTopics[x][topic] )
			self.topTerms.append( topTerms )
		
		self.termCount = len(self.termSet)
		self.topicCount = len(self.topicSet)
	
	def ReadDocTopicMixtures( self ):
		self.logger.info( 'Reading doc-topic matrix: %s', self.modelDocTopicMixtures )
		self.docSet = set()
		self.docsAndTopics = {}
		header = None
		with open( self.modelDocTopicMixtures, 'r' ) as f:
			for line in f:
				line = line.rstrip('\n').decode('utf-8')
				if header is None:
					assert line == "#doc name topic proportion ..."
					header = line
				else:
					fields = line.split( '\t' )
					docIndex = int(fields[0])
					docId = fields[1]
					topicKeys = [ int(key) for n, key in enumerate(fields[2:]) if n % 2 == 0 and key != '' ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n % 2 == 1 and value != '' ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if docId not in self.docSet:
							self.docSet.add( docId )
							self.docsAndTopics[ docId ] = [ 0.0 ] * self.topicCount
						self.docsAndTopics[ docId ][ topic ] = value
		
		self.docCount = len(self.docSet)
	
	def SaveToDB( self ):
		termList = sorted( self.termSet, key = lambda x : -self.termFreqs[x] )
		docList = sorted( self.docSet )
		topicList = sorted( self.topicSet )
		
		termTable = []
		docTable = []
		topicTable = []
		termLookup = {}
		docLookup = {}
		for index, term in enumerate(termList):
			termTable.append({
				'term_index' : index,
				'term_text' : term
			})
			termLookup[term] = index
		for index, docId in enumerate(docList):
			docTable.append({
				'doc_index' : index
			})
			docLookup[docId] = index
		for index, topic in enumerate(topicList):
			topicTable.append({
				'topic_index' : index,
				'topic_freq' : self.topicFreqs[ topic ],
				'topic_desc' : u', '.join( self.topTerms[topic][:5] ),
				'topic_top_terms' : self.topTerms[topic][:30]
			})
		termIndexes = self.ldaDB.db.terms.bulk_insert(termTable)
		docIndexes = self.ldaDB.db.docs.bulk_insert(docTable)
		topicIndexes = self.ldaDB.db.topics.bulk_insert(topicTable)

		termTopicMatrix = []
		docTopicMatrix = []
		for term in self.termsAndTopics:
			for topic, value in enumerate(self.termsAndTopics[term]):
				if value > MalletReader.THRESHOLD:
					termTopicMatrix.append({
						'term_index' : termLookup[term],
					 	'topic_index' : topic,
						'value' : value
					})
		for docId in self.docsAndTopics:
			for topic, value in enumerate(self.docsAndTopics[docId]):
				if value > MalletReader.THRESHOLD:
					docTopicMatrix.append({
						'doc_index' : docLookup[docId],
					 	'topic_index' : topic,
						'value' : value
					})
		termTopicMatrix.sort( key = lambda x : -x['value'] )
		docTopicMatrix.sort( key = lambda x : -x['value'] )
		self.ldaDB.db.term_topic_matrix.bulk_insert(termTopicMatrix)
		self.ldaDB.db.doc_topic_matrix.bulk_insert(docTopicMatrix)
