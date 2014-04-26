#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class LDAReader(object):
	"""
	lda_db = a SQLite3 database
	"""
	TOP_TERMS = 25
	TOP_DOCS = 50

	def __init__(self, lda_db):
		self.logger = logging.getLogger('termite')
		self.db = lda_db.db
		self.termList = []
		self.termTopicMatrix = []
		self.docList = []
		self.docTopicMatrix = []

	def SaveToDB( self ):
		self.logger.debug( '    Saving term_topic_matrix...' )
		table = self.db.term_topic_matrix
		table.bulk_insert(self.termTopicMatrix)

		self.logger.debug( '    Saving doc_topic_matrix...' )
		table = self.db.doc_topic_matrix
		table.bulk_insert(self.docTopicMatrix)

		self.logger.debug( '    Retrieving terms, documents, and topics...' )
		table = self.db.term_topic_matrix
		query = 'SELECT term_index, SUM(value) AS term_freq FROM {} GROUP BY term_index ORDER BY term_freq DESC'.format(table)
		termTable = self.db.executesql(query, as_dict=True)
		query = 'SELECT COUNT(DISTINCT term_index) FROM {}'.format(table)
		termCount = self.db.executesql(query)[0][0]

		table = self.db.doc_topic_matrix
		query = 'SELECT doc_index, SUM(value) AS doc_freq FROM {} GROUP BY doc_index ORDER BY doc_freq DESC'.format(table)
		docTable = self.db.executesql(query, as_dict=True)
		query = 'SELECT COUNT(DISTINCT doc_index) FROM {}'.format(table)
		docCount = self.db.executesql(query)[0][0]

		table = self.db.term_topic_matrix
		query = 'SELECT topic_index, SUM(value) AS topic_freq FROM {} GROUP BY topic_index ORDER BY topic_freq DESC'.format(table)
		topicTable = self.db.executesql(query, as_dict=True)
		query = 'SELECT COUNT(DISTINCT topic_index) FROM {}'.format(table)
		topicCount = self.db.executesql(query)[0][0]

		self.logger.debug( '    Retrieving top terms and top documents...' )
		table = self.db.term_topic_matrix
		topTerms = []
		for topicIndex in range(topicCount):
			where = (table.topic_index == topicIndex)
			orderby = table.rank
			limitby = (0, LDAReader.TOP_TERMS)
			topTerms.append([ d.term_index for d in self.db(where).select(table.term_index, orderby=orderby, limitby=limitby) ])
		table = self.db.doc_topic_matrix
		topDocs = []
		for topicIndex in range(topicCount):
			where = (table.topic_index == topicIndex)
			orderby = table.rank
			limitby = (0, LDAReader.TOP_DOCS)
			topDocs.append([ d.doc_index for d in self.db(where).select(table.doc_index, orderby=orderby, limitby=limitby) ])

		self.logger.debug( '    Saving terms...' )
		for index, d in enumerate(termTable):
			termIndex = d['term_index']
			d['term_text'] = self.termList[termIndex]
			d['rank'] = index + 1
		self.db.terms.bulk_insert(termTable)

		self.logger.debug( '    Saving docs...' )
		for index, d in enumerate(docTable):
			docIndex = d['doc_index']
			d['doc_id'] = self.docList[docIndex]
			d['rank'] = index + 1
		self.db.docs.bulk_insert(docTable)

		self.logger.debug( '    Saving topics...' )
		for index, d in enumerate(topicTable):
			topicIndex = d['topic_index']
			d['topic_label'] = u', '.join([ self.termList[n] for n in topTerms[topicIndex][:3] ])
			d['topic_desc'] = u', '.join([ self.termList[n] for n in topTerms[topicIndex][:5] ])
			d['top_terms'] = topTerms[topicIndex]
			d['top_docs'] = topDocs[topicIndex]
			d['rank'] = index + 1
		self.db.topics.bulk_insert(topicTable)
