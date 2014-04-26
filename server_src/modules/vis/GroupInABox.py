#!/usr/bin/env python

import os
import json
from core.HomeCore import HomeCore
from json import encoder as JsonEncoder

class GroupInABox(HomeCore):
	def __init__(self, request, response, corpus_db, lda_db):
		super(GroupInABox, self).__init__( request, response )
		JsonEncoder.FLOAT_REPR = lambda number : format( number, '.4g' )
		self.corpusDB = corpus_db.db
		self.ldaDB = lda_db.db

	def GetTermLimit(self):
		termLimit = self.GetNonNegativeIntegerParam( 'termLimit', 100 if self.IsMachineFormat() else 5 )
		self.params.update({
			'termLimit' : termLimit
		})
		return termLimit

	def Load(self):
		self.LoadTopTermsPerTopic()
		self.LoadTopicCovariance()
		self.CreateTempVocabTable()
		self.LoadTermPMI()
		self.LoadSentencePMI()
		self.DeleteTempVocabTable()
		
	def LoadTopTermsPerTopic( self ):
		termLimit = self.GetTermLimit()
		topicCount = self.ldaDB(self.ldaDB.topics).count()
		data = []
		self.vocab = set()
		for topicIndex in range(topicCount):
			query = """SELECT matrix.value AS freq, terms.term_text AS term
			FROM {MATRIX} AS matrix
			INNER JOIN {TERMS} AS terms ON matrix.term_index = terms.term_index
			WHERE matrix.topic_index = {TOPIC_INDEX}
			ORDER BY matrix.rank
			LIMIT {LIMIT}""".format(MATRIX=self.ldaDB.term_topic_matrix, TERMS=self.ldaDB.terms, LIMIT=termLimit, TOPIC_INDEX=topicIndex)
			rows = self.ldaDB.executesql(query, as_dict = True)
			data.append(rows)
			self.vocab.update(row['term'] for row in rows)
		self.content.update({
			'TopTermsPerTopic' : data
		})

	def LoadTopicCovariance( self ):
		topicCount = self.ldaDB(self.ldaDB.topics).count()
		table = self.ldaDB.topic_covariance
		rows = self.ldaDB().select( table.ALL, orderby = table.rank )
		data = [ [0.0] * topicCount for _ in range(topicCount) ]
		for row in rows:
			data[row.first_topic_index][row.second_topic_index] = row.value
		self.content.update({
			'TopicCovariance' : data
		})
	
	def CreateTempVocabTable( self ):
		self.corpusDB.executesql( 'DELETE FROM vocab;' )
		self.corpusDB.executesql( 'DELETE FROM vocab_text;' )
		self.corpusDB.vocab_text.bulk_insert( { 'term_text' : d } for d in self.vocab )
		query = """INSERT INTO {TARGET} (term_index, term_text)
			SELECT terms.term_index, terms.term_text
			FROM {TERMS} AS terms
			INNER JOIN {SOURCE} AS vocab ON terms.term_text = vocab.term_text""".format(
				TERMS=self.corpusDB.term_texts, SOURCE=self.corpusDB.vocab_text, TARGET=self.corpusDB.vocab)
		self.corpusDB.executesql(query)
	
	def DeleteTempVocabTable( self ):
		pass

	def LoadTermPMI( self ):
		query = """SELECT ref1.term_text AS first_term, ref2.term_text AS second_term, matrix.value
		FROM {MATRIX} AS matrix
		INNER JOIN {VOCAB} AS ref1 ON matrix.first_term_index = ref1.term_index
		INNER JOIN {VOCAB} AS ref2 ON matrix.second_term_index = ref2.term_index
		ORDER BY matrix.rank
		LIMIT 2500""".format(MATRIX=self.corpusDB.term_pmi, VOCAB=self.corpusDB.vocab)
		rows = self.corpusDB.executesql(query, as_dict=True)
		self.content.update({
			'TermPMI' : rows
		})

	def LoadSentencePMI( self ):
		query = """SELECT ref1.term_text AS first_term, ref2.term_text AS second_term, matrix.value
		FROM {MATRIX} AS matrix
		INNER JOIN {VOCAB} AS ref1 ON matrix.first_term_index = ref1.term_index
		INNER JOIN {VOCAB} AS ref2 ON matrix.second_term_index = ref2.term_index
		ORDER BY matrix.rank
		LIMIT 2500""".format(MATRIX=self.corpusDB.sentences_pmi, VOCAB=self.corpusDB.vocab)
		rows = self.corpusDB.executesql(query, as_dict=True)
		self.content.update({
			'SentencePMI' : rows
		})
