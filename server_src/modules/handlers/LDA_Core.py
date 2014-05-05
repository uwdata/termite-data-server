#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers.Home_Core import Home_Core

class LDA_Core(Home_Core):
	def __init__(self, request, response, lda_db):
		super(LDA_Core, self).__init__(request, response)
		self.ldaDB = lda_db
		self.db = lda_db.db
	
	def GetDocLimits(self):
		docOffset = self.GetNonNegativeIntegerParam('docOffset')
		docLimit = self.GetNonNegativeIntegerParam('docLimit')
		self.params.update({
			'docOffset' : docOffset,
			'docLimit' : docLimit
		})
		if docOffset is None:
			docOffset = 0
		if docLimit is None:
			docLimit = 5
		return docOffset, docLimit
	
	def GetTermLimits(self):
		termOffset = self.GetNonNegativeIntegerParam('termOffset')
		termLimit = self.GetNonNegativeIntegerParam('termLimit')
		self.params.update({
			'termOffset' : termOffset,
			'termLimit' : termLimit
		})
		if termOffset is None:
			termOffset = 0
		if termLimit is None:
			termLimit = 5
		return termOffset, termLimit
	
	def GetCellLimits(self):
		cellLimit = self.GetNonNegativeIntegerParam('cellLimit')
		self.params.update({
			'cellLimit' : cellLimit
		})
		if cellLimit is None:
			cellLimit = 100
		return cellLimit
	
	def GetTopicIndex(self):
		topicIndex = self.GetNonNegativeIntegerParam('topicIndex')
		self.params.update({
			'topicIndex' : topicIndex
		})
		if topicIndex is None:
			topicIndex = 0
		return topicIndex

	def LoadVocab(self):
		table = self.db.terms
		rows = self.db().select( table.term_text, orderby = table.rank )
		data = [ row.term_text for row in rows ]
		self.content.update({
			'Vocab' : data,
		})

	def LoadTerms(self):
		termOffset, termLimit = self.GetTermLimits()
		table = self.db.terms
		rows = self.db().select( table.ALL, orderby = table.rank, limitby = (termOffset, termOffset+termLimit) ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TermList' : rows,
			'TermOffset' : termOffset,
			'TermLimit' : termLimit,
			'TermCount' : self.db(table).count()
		})
		self.table = rows
		self.header = header

	def LoadDocs(self):
		docOffset, docLimit = self.GetDocLimits()
		table = self.db.docs
		rows = self.db().select( table.ALL, orderby = table.doc_index, limitby = (docOffset, docOffset+docLimit) ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'DocList' : rows,
			'DocOffset' : docOffset,
			'DocLimit' : docLimit,
			'DocCount' : self.db(table).count()
		})
		self.table = rows
		self.header = header

	def LoadTopics(self):
		table = self.db.topics
		rows = self.db().select( table.ALL, orderby = table.topic_index ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopicList' : rows,
			'TopicCount' : self.db(table).count()
		})
		self.table = rows
		self.header = header
	
	def LoadTermTopicMatrix(self):
		termOffset, termLimit = self.GetTermLimits()
		cellLimit = self.GetCellLimits()
		matrix = self.db.term_topic_matrix
		ref = self.db.terms
		query = """SELECT matrix.term_index AS term_index, topic_index, value, term_text FROM {MATRIX} AS matrix
			INNER JOIN {REF} AS terms ON matrix.term_index = terms.term_index
			WHERE {LB} <= terms.term_index AND terms.term_index < {UB}
			ORDER BY matrix.rank
			LIMIT {LIMIT}""".format(MATRIX = matrix, REF = ref, LB = termOffset, UB = termOffset+termLimit, LIMIT = cellLimit)
		rows = self.db.executesql(query, as_dict=True)
		header = [
			{ 'name' : 'term_index' , 'type' : matrix.term_index.type  },
			{ 'name' : 'term_text'  , 'type' : ref.term_text.type      },
			{ 'name' : 'topic_index', 'type' : matrix.topic_index.type },
			{ 'name' : 'value'      , 'type' : matrix.value.type       }
		]
		self.content.update({
			'TermTopicMatrix' : rows,
			'TermOffset' : termOffset,
			'TermLimit' : termLimit,
			'CellLimit' : cellLimit,
			'TermCount' : self.db(self.db.terms).count(),
			'TopicCount' : self.db(self.db.topics).count(),
			'CellCount' : self.db(matrix).count()
		})
		self.table = rows
		self.header = header

	def LoadDocTopicMatrix(self):
		docOffset, docLimit = self.GetDocLimits()
		cellLimit = self.GetCellLimits()
		matrix = self.db.doc_topic_matrix
		ref = self.db.docs
		query = """SELECT matrix.doc_index AS doc_index, topic_index, value, doc_id FROM {MATRIX} AS matrix
			INNER JOIN {REF} AS docs ON matrix.doc_index = docs.doc_index
			WHERE {LB} <= docs.doc_index AND docs.doc_index < {UB}
			ORDER BY matrix.rank
			LIMIT {LIMIT}""".format(MATRIX = matrix, REF = ref, LB = docOffset, UB = docOffset+docLimit, LIMIT = cellLimit)
		rows = self.db.executesql(query, as_dict=True)
		header = [
			{ 'name' : 'doc_index'  , 'type' : matrix.doc_index.type  },
			{ 'name' : 'doc_id'     , 'type' : ref.doc_id.type      },
			{ 'name' : 'topic_index', 'type' : matrix.topic_index.type },
			{ 'name' : 'value'      , 'type' : matrix.value.type       }
		]
		self.content.update({
			'DocTopicMatrix' : rows,
			'DocOffset' : docOffset,
			'DocLimit' : docLimit,
			'CellLimit' : cellLimit,
			'DocCount' : self.db(self.db.docs).count(),
			'TopicCount' : self.db(self.db.topics).count(),
			'CellCount' : self.db(matrix).count()
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
		topicIndex = self.GetTopicIndex()
		termOffset, termLimit = self.GetTermLimits()
		termCount = self.db(self.db.terms).count()
		matrix = self.db.term_topic_matrix
		table = self.db.terms
		inner_join = ( matrix.term_index == table.term_index )
		where = ( matrix.topic_index == topicIndex )
		rows = self.db( inner_join & where ).select( table.ALL, orderby = matrix.rank, limitby = (termOffset, termOffset+termLimit) ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopTerms' : rows,
			'TopicIndex' : topicIndex,
			'TermOffset' : termOffset,
			'TermLimit' : termLimit,
			'TermCount' : termCount
		})
		self.table = rows
		self.header = header

	def LoadTopDocs(self):
		self.LoadTopics()
		topicIndex = self.GetTopicIndex()
		docOffset, docLimit = self.GetDocLimits()
		docCount = self.db(self.db.docs).count()
		matrix = self.db.doc_topic_matrix
		table = self.db.docs
		inner_join = ( matrix.doc_index == table.doc_index )
		where = ( matrix.topic_index == topicIndex )
		rows = self.db( inner_join & where ).select( table.ALL, orderby = matrix.rank, limitby = (docOffset, docOffset+docLimit) ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'TopDocs' : rows,
			'TopicIndex' : topicIndex,
			'DocOffset' : docOffset,
			'DocLimit' : docLimit,
			'DocCount' : docCount
		})
		self.table = rows
		self.header = header
