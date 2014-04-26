#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class MalletReader():
	"""
	modelPath = a model folder containing files topic-word-weights.txt and doc-topic-mixtures.txt
	LDA_DB = a SQLite3 database
	"""
	
	FREQ_THRESHOLD = 3
	PROB_THRESHOLD = 0.01
	TOP_TERMS = 25
	TOP_DOCS = 50
	TOPIC_WORD_WEIGHTS_FILENAME = 'topic-word-weights.txt'
	DOC_TOPIC_MIXTURES_FILENAME = 'doc-topic-mixtures.txt'
	
	def __init__( self, modelPath, LDA_DB ):
		self.logger = logging.getLogger('termite')
		self.modelPath = modelPath
		self.modelTopicWordWeights = '{}/{}'.format( self.modelPath, MalletReader.TOPIC_WORD_WEIGHTS_FILENAME )
		self.modelDocTopicMixtures = '{}/{}'.format( self.modelPath, MalletReader.DOC_TOPIC_MIXTURES_FILENAME )
		self.db = LDA_DB.db
	
	def Execute(self):
		self.termList = []
		self.docList = []
		self.topicCount = 0
		self.termFreqs = {}
		self.docFreqs = {}
		self.topicFreqs = {}
		self.termsAndTopics = {}
		self.docsAndTopics = {}
		self.logger.info( 'Reading MALLET LDA output...' )
		self.ReadTopicWordWeights()
		self.ReadDocTopicMixtures()
		self.logger.info( 'Writing to database...' )
		self.SaveToDB()
	
	def ReadTopicWordWeights( self ):
		termSet = set()
		topicSet = set()
		self.logger.debug( '    Loading matrix: %s', self.modelTopicWordWeights )
		with open( self.modelTopicWordWeights, 'r' ) as f:
			for line in f:
				line = line.rstrip('\n').decode('utf-8')
				topicIndex, term, value = line.split('\t')
				topicIndex = int(topicIndex)
				value = float(value)
				if topicIndex not in topicSet:
					topicSet.add( topicIndex )
					self.topicFreqs[ topicIndex ] = 0.0
				if term not in termSet:
					termSet.add( term )
					self.termList.append( term )
					self.termFreqs[ term ] = 0.0
					self.termsAndTopics[ term ] = {}
				self.topicFreqs[ topicIndex ] += value
				self.termFreqs[ term ] += value
				self.termsAndTopics[ term ][ topicIndex ] = value
		self.termCount = len(termSet)
		self.topicCount = len(topicSet)
	
	def ReadDocTopicMixtures( self ):
		docSet = set()
		self.logger.debug( '    Loading matrix: %s', self.modelDocTopicMixtures )
		with open( self.modelDocTopicMixtures, 'r' ) as f:
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
						if docId not in docSet:
							docSet.add( docId )
							self.docList.append( docId )
							self.docFreqs[ docId ] = 0.0
							self.docsAndTopics[ docId ] = {}
						self.docFreqs[ docId ] += value
						self.docsAndTopics[ docId ][ topicIndex ] = value
		self.docCount = len(docSet)
	
	def SaveToDB( self ):
		termLookup = { term : termIndex for termIndex, term in enumerate(self.termList) }
		docLookup = { docId : docIndex for docIndex, docId in enumerate(self.docList) }
		
		self.logger.debug( '    Saving term_topic_matrix...' )
		termTopicMatrix = []
		for term in self.termsAndTopics:
			for topicIndex, value in enumerate(self.termsAndTopics[term]):
				if value > MalletReader.FREQ_THRESHOLD:
					termTopicMatrix.append({
						'term_index' : termLookup[term],
					 	'topic_index' : topicIndex,
						'value' : value,
						'rank' : 0
					})
		termTopicMatrix.sort( key = lambda d : -d['value'] )
		for rank, d in enumerate(termTopicMatrix):
			d['rank'] = rank+1
		self.db.term_topic_matrix.bulk_insert(termTopicMatrix)
		
		self.logger.debug( '    Saving doc_topic_matrix...' )
		docTopicMatrix = []
		for docId in self.docsAndTopics:
			for topicIndex, value in enumerate(self.docsAndTopics[docId]):
				if value > MalletReader.PROB_THRESHOLD:
					docTopicMatrix.append({
						'doc_index' : docLookup[docId],
					 	'topic_index' : topicIndex,
						'value' : value,
						'rank' : 0
					})
		docTopicMatrix.sort( key = lambda d : -d['value'] )
		for rank, d in enumerate(docTopicMatrix):
			d['rank'] = rank+1
		self.db.doc_topic_matrix.bulk_insert(docTopicMatrix)
		
		self.logger.debug( '    Retrieving top terms and documents...' )
		topTerms = []
		topDocs = []
		table = self.db.term_topic_matrix
		for topicIndex in range(self.topicCount):
			rows = self.db(table.topic_index==topicIndex).select(table.term_index, orderby=table.rank, limitby=(0,MalletReader.TOP_TERMS))
			topTerms.append([ row.term_index for row in rows ])
		table = self.db.doc_topic_matrix
		for topicIndex in range(self.topicCount):
			rows = self.db(table.topic_index==topicIndex).select(table.doc_index, orderby=table.rank, limitby=(0,MalletReader.TOP_DOCS))
			topDocs.append([ row.doc_index for row in rows ])
		
		self.logger.debug( '    Saving terms...' )
		termTable = []
		for termIndex, term in enumerate(self.termList):
			termTable.append({
				'term_index' : termIndex,
				'term_text' : term,
				'term_freq' : self.termFreqs[term],
				'rank' : 0
			})
		for rank, d in enumerate(termTable):
			d['rank'] = rank+1
		self.db.terms.bulk_insert(termTable)

		self.logger.debug( '    Saving docs...' )
		docTable = []
		for docIndex, docId in enumerate(self.docList):
			docTable.append({
				'doc_index' : docIndex,
				'doc_id' : docId,
				'doc_freq' : self.docFreqs[docId],
				'rank' : 0
			})
		for rank, d in enumerate(docTable):
			d['rank'] = rank+1
		self.db.docs.bulk_insert(docTable)

		self.logger.debug( '    Saving topics...' )
		topicTable = []
		for topicIndex in range(self.topicCount):
			topicTable.append({
				'topic_index' : topicIndex,
				'topic_freq'  : self.topicFreqs[topicIndex],
				'topic_label' : u', '.join([ self.termList[n] for n in topTerms[topicIndex][:3] ]),
				'topic_desc'  : u', '.join([ self.termList[n] for n in topTerms[topicIndex][:5] ]),
				'top_terms' : topTerms[topicIndex],
				'top_docs' : topDocs[topicIndex],
				'rank' : 0
			})
		for rank, d in enumerate(topicTable):
			d['rank'] = rank+1
		self.db.topics.bulk_insert(topicTable)
