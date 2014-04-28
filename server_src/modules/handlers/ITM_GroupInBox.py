#!/usr/bin/env python

import os
import json
from json import encoder as JsonEncoder
from db.LDA_DB import LDA_DB
from db.LDA_ComputeStats import LDA_ComputeStats
from handlers.Home_Core import Home_Core
from modellers.TreeTM import RefineLDA
from readers.TreeTMReader import TreeTMReader

class ITM_GroupInBox(Home_Core):
	def __init__(self, request, response, corpus_db, lda_db):
		super(ITM_GroupInBox, self).__init__(request, response)
		JsonEncoder.FLOAT_REPR = lambda number : format(number, '.4g')
		self.corpusDB = corpus_db.db
		self.ldaDB = lda_db.db

################################################################################

	def GetAction(self):
		action = self.GetStringParam( 'action' )
		self.params.update({
			'action' : action
		})
		return action

	def GetIterCount(self, app_model_path):
		filename = '{}/index.json'.format(app_model_path)
		with open(filename, 'r') as f:
			data = json.load(f, encoding='utf-8')
			entry = data['completedEntryID']
		filename = '{}/entry-{:06d}/states.json'.format(app_model_path, entry)
		with open(filename, 'r') as f:
			data = json.load(f, encoding='utf-8')
			iterCount = data['numIters']
		return iterCount

	def GetIters(self, iterCount):
		iters = self.GetNonNegativeIntegerParam( 'iters', None )
		self.params.update({
			'iters' : iters if iters is not None else iterCount
		})
		return iters

	def GetConstraints(self):
		mustLinksStr = self.GetStringParam('mustLinks')
		cannotLinksStr = self.GetStringParam('cannotLinks')
		keepTermsStr = self.GetStringParam('keepTerms')
		removeTermsStr =  self.GetStringParam('removeTerms')
		mustLinks = []
		cannotLinks = []
		keepTerms = {}
		removeTerms = []
		try:
			data = json.loads(mustLinksStr)
			if type(data) is list:
				mustLinks = [ [ d for d in dd if type(d) is unicode ] for dd in data if type(dd) is list ]
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(cannotLinksStr)
			if type(data) is list:
				cannotLinks = [ [ d for d in dd if type(d) is unicode ] for dd in data if type(dd) is list ]
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(keepTermsStr)
			if type(data) is dict:
				for key, value in data.iteritems():
					keepTerms = { int(key) : [ d for d in value if type(d) is unicode ] for key, value in data.iteritems() if type(value) is list }
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(removeTermsStr)
			if type(data) is list:
				removeTerms = [ d for d in data if type(d) is unicode ]
		except (ValueError, KeyError, TypeError):
			pass

		self.params.update({
			'mustLinks' : mustLinksStr,
			'cannotLinks' : cannotLinksStr,
			'keepTerms' : keepTermsStr,
			'removeTerms' : removeTermsStr
		})
		return mustLinks, cannotLinks, keepTerms, removeTerms

	def UpdateModel(self):
		app_path = self.request.folder
		app_model_path = '{}/data/treetm'.format(app_path)
		iterCount = self.GetIterCount(app_model_path)
		iters = self.GetIters(iterCount)
		mustLinks, cannotLinks, keepTerms, removeTerms = self.GetConstraints()
		action = self.GetAction()
		if action != 'train' or iters is None:
			iterCount = self.GetIterCount(app_model_path)
			self.content.update({
				'IterCount' : iterCount,
				'MustLinks' : mustLinks,
				'CannotLinks' : cannotLinks,
				'KeepTerms' : keepTerms,
				'RemoveTerms' : removeTerms
			})
		else:
			RefineLDA( app_model_path, numIters = iters, 
				mustLinks = mustLinks, cannotLinks = cannotLinks, keepTerms = keepTerms, removeTerms = removeTerms )
			with LDA_DB( isReset = True ) as lda_db:
				reader = TreeTMReader( lda_db, app_model_path )
				reader.Execute()
				computer = LDA_ComputeStats( lda_db )
				computer.Execute()
			iterCount = self.GetIterCount(app_model_path)
			self.content.update({
				'IterCount' : iterCount,
				'MustLinks' : mustLinks,
				'CannotLinks' : cannotLinks,
				'KeepTerms' : keepTerms,
				'RemoveTerms' : removeTerms
			})

################################################################################

	def GetTermLimit(self):
		termLimit = self.GetNonNegativeIntegerParam( 'termLimit', 100 if self.IsMachineFormat() else 5 )
		self.params.update({
			'termLimit' : termLimit
		})
		return termLimit

	def Load(self):
		self.UpdateModel()
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
