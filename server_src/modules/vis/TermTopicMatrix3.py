#!/usr/bin/env python

import json
import math
from handlers.Home_Core import Home_Core

class TermTopicMatrix3(Home_Core):
	def __init__(self, request, response, bow_db, lda_db):
		super(TermTopicMatrix3, self).__init__(request, response)
		self.bowDB = bow_db
		self.ldaDB = lda_db
		self.bow = bow_db.db
		self.lda = lda_db.db

	def GetTopics(self):
		table = self.lda.topics
		rows = self.lda().select( table.topic_index, orderby = table.topic_index, limitby = (0, 2000) )
		return [ 'Topic {}'.format(d.topic_index+1) for d in rows ]
	
	def GetTerms(self):
		table = self.lda.terms
		rows = self.lda().select( table.term_text, orderby = table.term_index, limitby = (0, 1000) )
		return [ d.term_text for d in rows ]
	
	def GetTermTopicMatrix(self):
		table = self.lda.term_topic_matrix
		rows = self.lda().select( table.term_index, table.topic_index, table.value, orderby = table.rank, limitby = (0, 250000) )
		return [{
			'rowIndex' : d['term_index'],
			'columnIndex' : d['topic_index'],
			'value' : d['value']
		} for d in rows]
