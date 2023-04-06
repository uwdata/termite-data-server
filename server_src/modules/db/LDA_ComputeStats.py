#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builtins import range
from builtins import object
import logging

class LDA_ComputeStats(object):

	def __init__(self, lda_db, corpus_db):
		self.logger = logging.getLogger('termite')
		self.db = lda_db.db
		self.ldaDB = lda_db
		self.corpusDB = corpus_db
		
		self.maxCoTopicCount = int(self.ldaDB.GetOption('max_co_topic_count'))

################################################################################

	def Execute(self):
		self.logger.info( 'Computing derived LDA topic model statistics...' )
		self.logger.info( '    max_co_topic_count = %s', self.maxCoTopicCount )
		self.ReadDocCount()
		self.ReadTopicCount()
		self.ReadDocTopicMatrix()
		self.ComputeTopicCooccurrences()
		self.ComputeTopicCovariance()
		self.WriteTopicCovariance()
		self.corpusDB.AddModel('lda', 'Topic Model')
	
	def ReadDocCount(self):
		count = self.db(self.db.docs).count()
		self.docCount = count
		
	def ReadTopicCount(self):
		count = self.db(self.db.topics).count()
		self.topicCount = count
		
	def ReadDocTopicMatrix(self):
		self.logger.debug( '    Loading doc_topic_matrix...' )
		table = self.db.doc_topic_matrix
		matrix = {}
		rows = self.db(table).select(table.doc_index, table.topic_index, table.value)
		for row in rows:
			doc_index = row.doc_index
			topic_index = row.topic_index
			value = row.value
			if doc_index not in matrix:
				matrix[doc_index] = {}
			matrix[doc_index][topic_index] = value
		self.docsAndTopics = matrix

	def ComputeTopicCooccurrences(self):
		self.logger.debug( '    Computing topic cooccurrences...' )
		matrix = [ [0.0] * self.topicCount for _ in range(self.topicCount) ]
		for docID, topicMixture in self.docsAndTopics.items():
			for i, iValue in topicMixture.items():
				for j, jValue in topicMixture.items():
					matrix[i][j] += iValue * jValue
		normalization = 1.0 / self.docCount if self.docCount > 1.0 else 1.0
		for i in range(self.topicCount):
			for j in range(self.topicCount):
				matrix[i][j] *= normalization

		data = []
		for i, row in enumerate(matrix):
			for j, value in enumerate(row):
				data.append({ 'first_topic_index' : i, 'second_topic_index' : j, 'value' : value, 'rank' : 0 })
		data.sort( key = lambda x : -x['value'] )
		for rank, d in enumerate(data):
			d['rank'] = rank+1
		data = data[:self.maxCoTopicCount]
		self.topicCooccurrences = data

	def ComputeTopicCovariance(self):
		self.logger.debug( '    Computing topic covariance...' )
		data = self.topicCooccurrences
		normalization = sum( d['value'] for d in data )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		for d in data:
			d['value'] *= normalization
		self.topicCovariance = data
	
	def WriteTopicCovariance(self):
		self.logger.debug( '    Saving topic_covariance...' )
		rows = self.topicCovariance
		self.logger.debug( '        inserting %d rows...', len(rows) )
		self.db.topic_covariance.bulk_insert(rows)
