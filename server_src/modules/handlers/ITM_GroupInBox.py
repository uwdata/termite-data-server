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
			RefineLDA( app_model_path, numIters = iters, mustLinks = mustLinks, cannotLinks = cannotLinks, keepTerms = keepTerms, removeTerms = removeTerms )
			with Corpus_DB() as corpsu_db:
				with LDA_DB( isReset = True ) as lda_db:
					reader = TreeTMReader( lda_db, app_model_path )
					reader.Execute()
					computer = LDA_ComputeStats( lda_db, corpus_db )
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
#		self.LoadSentencePMI()
		self.DeleteTempVocabTable()
		
	def LoadTopTermsPerTopic( self ):
		termLimit = self.GetTermLimit()
		topicCount = self.ldaDB(self.ldaDB.topics).count()
		data = []
		self.vocab = set()
		for topicIndex in range(topicCount):
			query = """SELECT matrix.value AS value, terms.term_text AS term
			FROM {MATRIX} AS matrix
			INNER JOIN {TERMS} AS terms ON matrix.term_index = terms.term_index
			WHERE matrix.topic_index = {TOPIC_INDEX}
			ORDER BY matrix.rank
			LIMIT {LIMIT}""".format(MATRIX=self.ldaDB.term_topic_matrix, TERMS=self.ldaDB.terms, LIMIT=termLimit, TOPIC_INDEX=topicIndex)
			rows = self.ldaDB.executesql(query, as_dict = True)
			data.append(rows)
			self.vocab.update(row['term'] for row in rows)
		self.content.update({
			'TopTermsPerTopic' : data,
			'TopicCount' : topicCount
		})

	def LoadTopicCovariance( self ):
		query = """SELECT first_topic_index AS source, second_topic_index AS target, value
		FROM {MATRIX} AS matrix
		WHERE source != target""".format(MATRIX=self.ldaDB.topic_covariance)
		rows = self.ldaDB.executesql(query, as_dict=True)
		for index, row in enumerate(rows):
			row['rank'] = index+1
		self.content.update({
			'TopicCovariance' : rows
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

	def GetMarginalProbs( self, table ):
		query = """SELECT probs.term_index AS term_index, probs.value AS term_prob
		FROM {PROBS} AS probs
		INNER JOIN {VOCAB} AS vocab ON probs.term_index = vocab.term_index
		WHERE term_prob > 0""".format(PROBS = table, VOCAB = self.corpusDB.vocab)
		rows = self.corpusDB.executesql( query, as_dict = True )
		probs = { row['term_index'] : row['term_prob'] for row in rows }
		return probs
	
	def GetSparseJointProbs( self, table ):
		query = """SELECT ref1.term_text AS source, ref2.term_text AS target, matrix.first_term_index AS source_index, matrix.second_term_index AS target_index, matrix.value AS value
		FROM {MATRIX} AS matrix
		INNER JOIN {VOCAB} AS ref1 ON matrix.first_term_index = ref1.term_index
		INNER JOIN {VOCAB} AS ref2 ON matrix.second_term_index = ref2.term_index
		ORDER BY matrix.rank
		LIMIT 2000""".format(MATRIX = table, VOCAB = self.corpusDB.vocab)
		rows = self.corpusDB.executesql( query, as_dict = True )
		return rows
	
	def ComputePMI( self, marginalProbs, sparseJointProbs ):
		data = []
		for d in sparseJointProbs:
			source = d['source_index']
			target = d['target_index']
			value = d['value']
			if source in marginalProbs:
				if target in marginalProbs:
					pmi = value / marginalProbs[source] / marginalProbs[target]
					data.append({
						'source' : d['source'],
						'target' : d['target'],
						'value' : pmi,
						'rank' : 0
					})
		data.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(data):
			d['rank'] = index+1
		return data
		
	def LoadTermPMI(self):
		marginals = self.GetMarginalProbs( self.corpusDB.term_probs )
		joints = self.GetSparseJointProbs( self.corpusDB.term_co_probs )
		rows = self.ComputePMI( marginals, joints )
		self.content.update({
			'TermPMI' : rows
		})

	def LoadSentencePMI(self):
		marginals = self.GetMarginalProbs( self.corpusDB.term_probs )
		joints = self.GetSparseJointProbs( self.corpusDB.sentences_co_probs )
		rows = self.ComputePMI( marginals, joints )
		self.content.update({
			'SentencePMI' : rows
		})
