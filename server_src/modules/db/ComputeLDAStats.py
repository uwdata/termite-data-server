#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class ComputeLDAStats():

	def __init__( self, ldaDB, ldaStatsDB ):
		self.logger = logging.getLogger('termite')
		self.ldaDB = ldaDB
		self.ldaStatsDB = ldaStatsDB

	def Execute( self ):
		self.logger.info( 'Computing derived LDA statistics...' )
		self.ReadDocCount()
		self.ReadTopicCount()
		self.ReadDocTopicMatrix()
		self.ComputeTopicCooccurrenceAndCovariance()
		self.WriteTopicCooccurrence()
		self.WriteTopicCovariance()
	
	def ReadDocCount(self):
		count = self.ldaDB.db( self.ldaDB.db.docs ).count()
		self.docCount = count
		
	def ReadTopicCount(self):
		count = self.ldaDB.db( self.ldaDB.db.topics ).count()
		self.topicCount = count
		
	def ReadDocTopicMatrix( self ):
		self.logger.debug( '    Loading doc_topic_matrix...' )
		matrix = {}
		rows = self.ldaDB.db( self.ldaDB.db.doc_topic_matrix ).select( self.ldaDB.db.doc_topic_matrix.doc_index, self.ldaDB.db.doc_topic_matrix.topic_index, self.ldaDB.db.doc_topic_matrix.value )
		for row in rows:
			doc_index = row.doc_index
			topic_index = row.topic_index
			value = row.value
			if doc_index not in matrix:
				matrix[doc_index] = {}
			matrix[doc_index][topic_index] = value
		self.docsAndTopics = matrix

	def ComputeTopicCooccurrenceAndCovariance( self ):
		self.logger.debug( '    Computing topic cooccurrences...' )
		matrix = [ [0.0] * self.topicCount for _ in range(self.topicCount) ]
		for docID, topicMixture in self.docsAndTopics.iteritems():
			for i in range(self.topicCount):
				if i in topicMixture:
					for j in range(self.topicCount):
						if j in topicMixture:
							matrix[i][j] += topicMixture[i] * topicMixture[j]
		normalization = 1.0 / self.docCount if self.docCount > 0 else 1
		matrix = [ [ matrix[i][j] * normalization for j in range(self.topicCount) ] for i in range(self.topicCount) ]

		data = []
		for i, row in enumerate(matrix):
			for j, value in enumerate(row):
				data.append({ 'first_topic_index' : i, 'second_topic_index' : j, 'value' : value, 'rank' : 0 })
		self.topicCooccurrences = data
		self.topicCooccurrences.sort( key = lambda x : -x['value'] )
		for rank, d in enumerate(self.topicCooccurrences):
			d['rank'] = rank+1

		self.logger.debug( '    Computing topic covariance...' )
		normalization = sum( d['value'] for d in data )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		self.topicCovariance = [ {
			'first_topic_index' : d['first_topic_index'], 
			'second_topic_index' : d['second_topic_index'], 
			'value' : d['value'] * normalization, 
			'rank' : d['rank']
		} for d in data ]

	def WriteTopicCooccurrence( self ):
		self.logger.debug( '    Saving topic_cooccurrences...' )
		self.ldaStatsDB.db.topic_cooccurrences.bulk_insert( self.topicCooccurrences )
		
	def WriteTopicCovariance( self ):
		self.logger.debug( '    Saving topic_covariance...' )
		self.ldaStatsDB.db.topic_covariance.bulk_insert( self.topicCovariance )
