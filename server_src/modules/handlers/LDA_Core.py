#!/usr/bin/env python

import os
import json
from handlers.Home_Core import Home_Core

class LDA_Core(Home_Core):
	def __init__(self, request, response, lda_db):
		super(LDA_Core, self).__init__(request, response)
		self.db = lda_db.db
	
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
		self.content.update({
			'TermIndex' : rows,
			'TermCount' : self.db(table).count()
		})
		self.table = rows
		self.header = header

	def LoadDocs(self):
		doc_limits = self.GetDocLimits()
		table = self.db.docs
		rows = self.db().select( table.ALL, orderby = table.doc_index, limitby = doc_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'DocIndex' : rows,
			'DocCount' : self.db(table).count()
		})
		self.table = rows
		self.header = header

	def LoadTopics(self):
		table = self.db.topics
		rows = self.db().select( table.ALL, orderby = table.topic_index ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopicIndex' : rows,
			'TopicCount' : self.db(table).count()
		})
		self.table = rows
		self.header = header
	
	def LoadTermTopicMatrix(self):
		term_limits = self.GetTermLimits()
		matrix = self.db.term_topic_matrix
		ref = self.db.terms
		query = """SELECT matrix.term_index AS term_index, topic_index, value, term_text FROM {MATRIX} AS matrix
			INNER JOIN {REF} AS terms ON matrix.term_index = terms.term_index
			WHERE {LB} <= terms.term_index AND terms.term_index < {UB}
			ORDER BY matrix.rank""".format(MATRIX = matrix, REF = ref, LB = term_limits[0], UB = term_limits[1])
		rows = self.db.executesql(query, as_dict=True)
		header = [
			{ 'name' : 'term_index' , 'type' : matrix.term_index.type  },
			{ 'name' : 'term_text'  , 'type' : ref.term_text.type      },
			{ 'name' : 'topic_index', 'type' : matrix.topic_index.type },
			{ 'name' : 'value'      , 'type' : matrix.value.type       }
		]
		self.content.update({
			'TermTopicMatrix' : rows,
			'TermCount' : self.db(self.db.terms).count(),
			'TopicCount' : self.db(self.db.topics).count(),
			'CellCount' : self.db(matrix).count()
		})
		self.table = rows
		self.header = header

	def LoadDocTopicMatrix(self):
		doc_limits = self.GetDocLimits()
		matrix = self.db.doc_topic_matrix
		ref = self.db.docs
		query = """SELECT matrix.doc_index AS doc_index, topic_index, value, doc_id FROM {MATRIX} AS matrix
			INNER JOIN {REF} AS docs ON matrix.doc_index = docs.doc_index
			WHERE {LB} <= docs.doc_index AND docs.doc_index < {UB}
			ORDER BY matrix.rank""".format(MATRIX = matrix, REF = ref, LB = doc_limits[0], UB = doc_limits[1])
		rows = self.db.executesql(query, as_dict=True)
		header = [
			{ 'name' : 'doc_index'  , 'type' : matrix.doc_index.type  },
			{ 'name' : 'doc_id'     , 'type' : ref.doc_id.type      },
			{ 'name' : 'topic_index', 'type' : matrix.topic_index.type },
			{ 'name' : 'value'      , 'type' : matrix.value.type       }
		]
		self.content.update({
			'DocTopicMatrix' : rows,
			'DocCount' : self.db(self.db.docs).count(),
			'TopicCount' : self.db(self.db.topics).count(),
			'CellCount' : self.db(matrix).count()
		})
		self.table = rows
		self.header = header
	
	def LoadTopicCooccurrences(self):
		table = self.db.topic_cooccurrences
		rows = self.db().select( table.ALL, orderby = table.rank ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopicCooccurrences' : rows,
			'TopicCount' : self.db(self.db.topics).count()
		})
		self.table = rows
		self.header = header

	def LoadTopicCovariance(self):
		table = self.db.topic_covariance
		rows = self.db().select( table.ALL, orderby = table.rank ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopicCovariance' : rows,
			'TopicCount' : self.db(self.db.topics).count()
		})
		self.table = rows
		self.header = header

	def LoadTopTerms(self):
		self.LoadTopics()
		topic_index = self.GetTopicIndex()
		term_limits = self.GetTermLimits()
		matrix = self.db.term_topic_matrix
		table = self.db.terms
		inner_join = ( matrix.term_index == table.term_index )
		where = ( matrix.topic_index == topic_index )
		rows = self.db( inner_join & where ).select( table.ALL, orderby = matrix.rank, limitby = term_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopTerms' : rows
		})
		self.table = rows
		self.header = header

	def LoadTopDocs(self):
		self.LoadTopics()
		topic_index = self.GetTopicIndex()
		doc_limits = self.GetDocLimits()
		matrix = self.db.doc_topic_matrix
		table = self.db.docs
		inner_join = ( matrix.doc_index == table.doc_index )
		where = ( matrix.topic_index == topic_index )
		rows = self.db( inner_join & where ).select( table.ALL, orderby = matrix.rank, limitby = doc_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopDocs' : rows
		})
		self.table = rows
		self.header = header
