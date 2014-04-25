#!/usr/bin/env python

import os
import json
from core.HomeCore import HomeCore

class LDACore( HomeCore ):
	def __init__( self, request, response, lda_db, ldaStats_db ):
		super( LDACore, self ).__init__( request, response )
		self.db = lda_db.db
		self.stats = ldaStats_db.db
	
	def GetParam( self, key ):
		if key == 'docOffset':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		if key == 'docLimit':
			if self.IsMachineFormat():
				value = self.GetNonNegativeIntegerParam( key, 100 )
			else:
				value = self.GetNonNegativeIntegerParam( key, 5 )
			self.params.update({ key : value })
		
		if key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		if key == 'termLimit':
			if self.IsMachineFormat():
				value = self.GetNonNegativeIntegerParam( key, 100 )
			else:
				value = self.GetNonNegativeIntegerParam( key, 5 )
			self.params.update({ key : value })
		
		if key == 'topicIndex':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		
		if key == 'rank':
			value = self.GetNonNegativeFloatParam( key, 1000 )
			self.params.update({ key : value })
			
		return value
	
	def LoadTermIndex( self ):
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		limits = (termOffset, termOffset+termLimit)
		
		# Load from DB
		rows = self.db(self.db.terms).select(self.db.terms.ALL, orderby=self.db.terms.term_index, limitby=limits)
		table = [ {
			'index' : row.term_index,
			'text' : row.term_text
		} for row in rows ]
		header = [
			{ 'name' : 'index', 'type' : 'integer' },
			{ 'name' : 'text', 'type' : 'string' } 
		]
		termCount = len(table)
		termMaxCount = self.db(self.db.terms).count()
		
		# Responses
		self.content.update({
			'TermIndex' : table,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount
		})
		self.table = table
		self.header = header

	def LoadDocIndex( self ):
		# Parameters
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		limits = (docOffset, docOffset+docLimit)
		
		# Load from DB
		rows = self.db(self.db.docs).select(self.db.docs.ALL, orderby=self.db.docs.doc_index, limitby=limits)
		table = [ {
			'index' : row.doc_index
		} for row in rows ]
		header = [
			{ 'name' : 'index', 'type' : 'integer' }
		]
		docCount = len(table)
		docMaxCount = self.db(self.db.docs).count()

		# Responses
		self.content.update({
			'DocIndex' : table,
			'DocCount' : docCount,
			'DocMaxCount' : docMaxCount
		})
		self.table = table
		self.header = header

	def LoadTopicIndex( self ):
		# Load from DB
		rows = self.db(self.db.topics).select(self.db.topics.ALL, orderby=self.db.topics.topic_index)
		table = [ {
			'index' : row.topic_index,
			'desc' : row.topic_desc
		} for row in rows ]
		header = [
			{ 'name' : 'index', 'type' : 'integer' },
			{ 'name' : 'desc', 'type' : 'string' }
		]
		topicCount = len(table)

		# Responses
		self.content.update({
			'TopicIndex' : table,
			'TopicCount' : topicCount,
			'TopicMaxCount' : topicCount,
		})
		self.table = table
		self.header = header
	
	def LoadTermTopicMatrix( self ):
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		
		# Load from DB
		inner_join = (self.db.term_topic_matrix.term_index == self.db.terms.term_index)
		limits = (termOffset <= self.db.terms.term_index) & (self.db.terms.term_index < termOffset+termLimit)
		rows = self.db(inner_join & limits).select(orderby=self.db.term_topic_matrix.rank)
		table = [ {
			'term' : row.terms.term_text,
			'topic' : row.term_topic_matrix.topic_index,
			'value' : row.term_topic_matrix.value
		} for row in rows ]
		header = [
			{ 'name' : 'term', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'integer' },
			{ 'name' : 'value', 'type' : 'real' }
		]
		cellCount = len(table)
		cellMaxCount = self.db(self.db.term_topic_matrix).count()

		# Responses
		self.content.update({
			'TermTopicMatrix' : table,
			'CellCount' : cellCount,
			'CellMaxCount' : cellMaxCount
		})
		self.table = table
		self.header = header

	def LoadDocTopicMatrix( self ):
		# Parameters
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		
		# Load from DB
		inner_join = (self.db.doc_topic_matrix.doc_index == self.db.docs.doc_index)
		limits = (docOffset <= self.db.docs.doc_index) & (self.db.docs.doc_index < docOffset+docLimit)
		rows = self.db(inner_join & limits).select(orderby=self.db.doc_topic_matrix.rank)
		table = [ {
			'doc_index' : row.docs.doc_index,
			'topic' : row.doc_topic_matrix.topic_index,
			'value' : row.doc_topic_matrix.value
		} for row in rows ]
		header = [
			{ 'name' : 'doc_index', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'integer' },
			{ 'name' : 'value', 'type' : 'real' }
		]
		cellCount = len(table)
		cellMaxCount = self.db(self.db.doc_topic_matrix).count()
		
		# Responses
		self.content.update({
			'DocTopicMatrix' : table,
			'CellCount' : cellCount,
			'CellMaxCount' : cellMaxCount
		})
		self.table = table
		self.header = header
	
	def LoadTopicCooccurrence( self ):
		# Load from DB
		rows = self.stats(self.stats.topic_cooccurrences).select()
		table = [ {
			'firstTopic' : row.first_topic_index,
			'secondTopic' : row.second_topic_index,
			'value' : row.value
		} for row in rows ]
		header = [
			{ 'name' : 'firstTopic', 'type' : 'integer' },
			{ 'name' : 'secondTopic', 'type' : 'integer' },
			{ 'name' : 'value', 'type' : 'real' }
		]

		# Responses
		self.content.update({
			'TopicCooccurrence' : table
		})
		self.table = table
		self.header = header

	def LoadTopicCovariance( self ):
		# Load from DB
		rows = self.stats(self.stats.topic_covariance).select()
		table = [ {
			'firstTopic' : row.first_topic_index,
			'secondTopic' : row.second_topic_index,
			'value' : row.value
		} for row in rows ]
		header = [
			{ 'name' : 'firstTopic', 'type' : 'integer' },
			{ 'name' : 'secondTopic', 'type' : 'integer' },
			{ 'name' : 'value', 'type' : 'real' }
		]
		
		# Responses
		self.content.update({
			'TopicCovariance' : table
		})
		self.table = table
		self.header = header
