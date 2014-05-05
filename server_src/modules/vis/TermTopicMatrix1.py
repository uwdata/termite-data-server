#!/usr/bin/env python

import json
import math
from handlers.Home_Core import Home_Core

class TermTopicMatrix1(Home_Core):
	def __init__(self, request, response, bow_db, lda_db):
		super(TermTopicMatrix1, self).__init__(request, response)
		self.bowDB = bow_db
		self.ldaDB = lda_db
		self.bow = bow_db.db
		self.lda = lda_db.db

	def GetStateModel(self):
		table = self.lda.topics
		rows = self.lda().select(table.topic_index, table.topic_label, orderby=table.topic_index)
		data = {
			'topicIndex' : [ {
				'color' : 'default',
				'id' : row.topic_index,
#				'name' : row.topic_label,
				'name' : 'Topic {}'.format(n+1),
				'position' : n,
				'selected' : False
			} for n, row in enumerate(rows) ]
		}
		return data

	def GetSeriatedTermTopicProbabilityModel(self):
		termLimit = 500
		data = {}
		
		table = self.lda.terms
		query = """SELECT term_text FROM {TABLE}
		WHERE rank <= {UB}
		ORDER BY rank""".format(TABLE = table, UB = termLimit)
		rows = self.lda.executesql(query, as_dict=True)
		data['termIndex'] = [ row['term_text'] for row in rows ]
		
		table = self.lda.topics
		query = """SELECT topic_index, topic_label FROM {TABLE}
		ORDER BY topic_index""".format(TABLE = table)
		rows = self.lda().select(table.topic_index, table.topic_label, orderby=table.topic_index)
		data['topicIndex'] = [ row.topic_label for row in rows ]
		data['topicMapping'] = [ n for n, row in enumerate(rows) ]
		topicCount = len(rows)
		
		table = self.lda.term_topic_matrix
		ref = self.lda.terms
		query = """SELECT t.rank as term_rank, topic_index AS topic_index, value AS value FROM {TABLE} AS m
			INNER JOIN {REF} AS t ON m.term_index = t.term_index
			WHERE t.rank <= {UB}
			ORDER BY t.rank""".format(TABLE = table, REF = ref, UB = termLimit)
		rows = self.lda.executesql(query, as_dict=True)
		matrix = [ [0.0] * topicCount for _ in range(termLimit) ]
		for row in rows:
			matrix[row['term_rank']-1][row['topic_index']] = row['value']
		data['matrix'] = matrix
		return data

	def GetFilteredTermTopicProbabilityModel(self):
		termLimit = 500
		data = {}

		table = self.lda.terms
		query = """SELECT term_text, term_freq, rank AS term_rank FROM {TABLE}
		WHERE rank <= {UB}
		ORDER BY rank""".format(TABLE = table, UB = termLimit)
		rows = self.lda.executesql(query, as_dict=True)
		data['termOrderMap'] = { row['term_text'] : row['term_rank']-1 for row in rows }
		data['termRankMap'] = { row['term_text'] : row['term_rank']-1 for row in rows }
		termTexts = [ row['term_text'] for row in rows ]
		termFreqs = { row['term_text'] : row['term_freq'] for row in rows }
		
		table = self.lda.topics
		topicCount = self.lda(table).count()

		table = self.lda.term_topic_matrix
		ref = self.lda.terms
		query = """SELECT t.rank as term_rank, topic_index AS topic_index, value AS value FROM {TABLE} AS m
			INNER JOIN {REF} AS t ON m.term_index = t.term_index
			WHERE t.rank <= {UB}
			ORDER BY t.rank""".format(TABLE = table, REF = ref, UB = termLimit)
		rows = self.lda.executesql(query, as_dict=True)
		matrix = [ [0.0] * topicCount for _ in range(termLimit) ]
		for row in rows:
			matrix[row['term_rank']-1][row['topic_index']] = row['value']
		termDistinctiveness = {}
		termSaliency = {}
		for i, row in enumerate(matrix):
			normalization = 1.0 / sum(row) if sum(row) > 0 else 1.0
			normalized_row = [ d * normalization for d in row ]
			q = 1.0 / topicCount
			value = sum([ p * math.log(p) - p * math.log(q) if p > 0 else 0 for p in normalized_row ])
			if i < len(termTexts):
				termText = termTexts[i]
				termDistinctiveness[termText] = value
				termSaliency[termText] = termFreqs[termText] * value
		data['termDistinctivenessMap'] = termDistinctiveness
		data['termSaliencyMap'] = termSaliency
		return data

	def GetTermFrequencyModel(self):
		termLimit = 500
		data = {}

		table = self.lda.terms
		query = """SELECT term_text, term_freq FROM {TABLE}
		WHERE rank <= {UB}
		ORDER BY rank""".format(TABLE = table, UB = termLimit)
		rows = self.lda.executesql(query, as_dict=True)
		data['termIndex'] = [ row['term_text'] for row in rows ]
		data['termFreqMap'] = { row['term_text'] : row['term_freq'] for row in rows }

		table = self.lda.topics
		query = """SELECT topic_index, topic_label FROM {TABLE}
		ORDER BY topic_index""".format(TABLE = table)
		rows = self.lda().select(table.topic_index, table.topic_label, orderby=table.topic_index)
#		data['topicIndex'] = [ row.topic_label for row in rows ]
		data['topicIndex'] = [ 'Topic {}'.format(n+1) for n, _ in enumerate(rows) ]
		data['topicMapping'] = [ n for n, row in enumerate(rows) ]
		topicCount = len(rows)

		table = self.lda.term_topic_matrix
		ref = self.lda.terms
		query = """SELECT t.rank as term_rank, topic_index AS topic_index, value AS value FROM {TABLE} AS m
			INNER JOIN {REF} AS t ON m.term_index = t.term_index
			WHERE t.rank <= {UB}
			ORDER BY t.rank""".format(TABLE = table, REF = ref, UB = termLimit)
		rows = self.lda.executesql(query, as_dict=True)
		matrix = [ [0.0] * topicCount for _ in range(termLimit) ]
		for row in rows:
			matrix[row['term_rank']-1][row['topic_index']] = row['value']
		data['matrix'] = matrix
		return data
