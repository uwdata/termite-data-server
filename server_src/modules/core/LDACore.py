#!/usr/bin/env python

import os
import json
from core.HomeCore import HomeCore

class LDACore(HomeCore):
	def __init__(self, request, response, lda_db, ldaStats_db):
		super( LDACore, self ).__init__( request, response )
		self.db = lda_db.db
		self.stats = ldaStats_db.db
	
	def GetDocLimits(self):
		docOffset = self.GetNonNegativeIntegerParam( 'docOffset', 0 )
		docLimit = self.GetNonNegativeIntegerParam( 'docLimit', 100 if self.IsMachineFormat() else 5 )
		self.params.update({
			'docOffset' : docOffset,
			'docLimit' : docLimit
		})
		return docOffset, docOffset+docLimit
	
	def GetTermLimits(self):
		termOffset = self.GetNonNegativeIntegerParam( 'termOffset', 0 )
		termLimit = self.GetNonNegativeIntegerParam( 'termLimit', 100 if self.IsMachineFormat() else 5 )
		self.params.update({
			'termOffset' : termOffset,
			'termLimit' : termLimit
		})
		return termOffset, termOffset+termLimit
	
	def GetTopicIndex(self):
		topicIndex = self.GetNonNegativeIntegerParam( 'topicIndex', 0 )
		self.params.update({
			'topicIndex' : topicIndex
		})
		return topicIndex
	
	def LoadTerms(self):
		term_limits = self.GetTermLimits()
		table = self.db.terms
		rows = self.db().select( table.ALL, orderby = table.rank, limitby = term_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		count = self.db(table).count()
		self.content.update({
			'TermIndex' : rows,
			'TermCount' : count
		})
		self.table = rows
		self.header = header

	def LoadDocs(self):
		doc_limits = self.GetDocLimits()
		table = self.db.docs
		rows = self.db().select( table.ALL, orderby = table.doc_index, limitby = doc_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		count = self.db(table).count()
		self.content.update({
			'DocIndex' : rows,
			'DocCount' : count
		})
		self.table = rows
		self.header = header

	def LoadTopics(self):
		table = self.db.topics
		rows = self.db().select( table.ALL, orderby = table.topic_index ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		count = self.db(table).count()
		self.content.update({
			'TopicIndex' : rows,
			'TopicCount' : count
		})
		self.table = rows
		self.header = header
	
	def LoadTermTopicMatrix(self):
		term_limits = self.GetTermLimits()
		table = self.db.term_topic_matrix
		ref = self.db.terms
		inner_join = ( table.term_index == ref.term_index )
		where = ( term_limits[0] <= table.term_index ) & ( table.term_index < term_limits[1] )
		rows = self.db( inner_join & where ).select( table.ALL, orderby = table.rank ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		count = self.db(table).count()
		self.content.update({
			'TermTopicMatrix' : rows,
			'CellCount' : count,
		})
		self.table = rows
		self.header = header

	def LoadDocTopicMatrix(self):
		doc_limits = self.GetDocLimits()
		table = self.db.doc_topic_matrix
		ref = self.db.docs
		inner_join = ( table.doc_index == ref.doc_index )
		where = ( doc_limits[0] <= table.doc_index ) & ( table.doc_index < doc_limits[1] )
		rows = self.db( inner_join & where ).select( table.ALL, orderby = table.rank ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		count = self.db(table).count()
		self.content.update({
			'DocTopicMatrix' : rows,
			'CellCount' : count
		})
		self.table = rows
		self.header = header
	
	def LoadTopicCooccurrences(self):
		table = self.stats.topic_cooccurrences
		rows = self.stats().select( table.ALL, orderby = table.rank ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopicCooccurrences' : rows
		})
		self.table = rows
		self.header = header

	def LoadTopicCovariance(self):
		table = self.stats.topic_covariance
		rows = self.stats().select( table.ALL, orderby = table.rank ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopicCovariance' : rows
		})
		self.table = rows
		self.header = header

	def LoadTopTerms(self):
		topic_index = self.GetTopicIndex()
		term_limits = self.GetTermLimits()
		matrix = self.db.term_topic_matrix
		table = self.db.terms
		inner_join = ( matrix.term_index == table.term_index )
		where = ( matrix.topic_index == topic_index )
		rows = self.db( inner_join & where ).select( table.ALL, matrix.ALL, orderby = matrix.rank, limitby = term_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopTerms' : rows
		})
		self.table = rows
		self.header = header

	def LoadTopDocs(self):
		topic_index = self.GetTopicIndex()
		doc_limits = self.GetDocLimits()
		matrix = self.db.doc_topic_matrix
		table = self.db.docs
		inner_join = ( matrix.doc_index == table.doc_index )
		where = ( matrix.topic_index == topic_index )
		rows = self.db( inner_join & where ).select( table.ALL, matrix.ALL, orderby = matrix.rank, limitby = doc_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopDocs' : rows
		})
		self.table = rows
		self.header = header
