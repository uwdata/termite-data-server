#!/usr/bin/env python

import os
import json
from json import encoder as JsonEncoder
from db.Corpus_DB import Corpus_DB
from db.LDA_DB import LDA_DB
from db.LDA_ComputeStats import LDA_ComputeStats
from handlers.Home_Core import Home_Core
from modellers.TreeTM import RefineLDA, InspectLDA
from readers.TreeTMReader import TreeTMReader

class GroupInBox(Home_Core):
	def __init__(self, request, response, corpus_db, bow_db, lda_db):
		super(GroupInBox, self).__init__(request, response)
		JsonEncoder.FLOAT_REPR = lambda number : format(number, '.4g')
		self.corpusDB = corpus_db
		self.bowDB = bow_db
		self.ldaDB = lda_db
		self.bow = bow_db.db
		self.db = lda_db.db

################################################################################

	def GetAction(self):
		action = self.GetStringParam('action')
		self.params.update({
			'action' : action
		})
		if action is None or action != 'train':
			action = ''
		return action

	def GetIters(self, iterCount):
		iters = self.GetNonNegativeIntegerParam('iters')
		self.params.update({
			'iters' : iters if iters is not None else iterCount
		})
		return iters

	def GetConstraints(self):
		mustLinksStr = self.GetStringParam('mustLinks')
		cannotLinksStr = self.GetStringParam('cannotLinks')
		keepTermsStr = self.GetStringParam('keepTerms')
		removeTermsStr =  self.GetStringParam('removeTerms')
		self.params.update({
			'mustLinks' : mustLinksStr,
			'cannotLinks' : cannotLinksStr,
			'keepTerms' : keepTermsStr,
			'removeTerms' : removeTermsStr
		})
		print "constraints as received"
		print mustLinksStr
		print cannotLinksStr
		print keepTermsStr
		print removeTermsStr
		mustLinks = None
		cannotLinks = None
		keepTerms = None
		removeTerms = None
		try:
			data = json.loads(mustLinksStr, encoding='utf8')
			if type(data) is list:
				mustLinks = [ [ d for d in dd if type(d) is unicode ] for dd in data if type(dd) is list ]
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(cannotLinksStr, encoding='utf8')
			if type(data) is list:
				cannotLinks = [ [ d for d in dd if type(d) is unicode ] for dd in data if type(dd) is list ]
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(keepTermsStr, encoding='utf8')
			if type(data) is dict:
				for key, value in data.iteritems():
					keepTerms = { int(key[5:]) : [ d for d in value if type(d) is unicode ] for key, value in data.iteritems() if type(value) is list }
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(removeTermsStr, encoding='utf8')
			if type(data) is list:
				removeTerms = [ d for d in data if type(d) is unicode ]
		except (ValueError, KeyError, TypeError):
			pass
		print "constraints sanitized"
		print mustLinks
		print cannotLinks
		print keepTerms
		print removeTerms
		return mustLinks, cannotLinks, keepTerms, removeTerms

	def UpdateModel(self):
		app_path = self.request.folder
		app_model_path = '{}/data/treetm'.format(app_path)
		action = self.GetAction()
		reader = InspectLDA( app_model_path )
		currIter = reader.Iters()
		finalIter = self.GetIters(currIter)
		mustLinks, cannotLinks, keepTerms, removeTerms = self.GetConstraints()
		if mustLinks is None:
			mustLinks = reader.MustLinks()
		if cannotLinks is None:
			cannotLinks = reader.CannotLinks()
		if keepTerms is None:
			keepTerms = reader.KeepTerms()
		if removeTerms is None:
			removeTerms = reader.RemoveTerms()
		if action == 'train' and finalIter is not None and finalIter > currIter:
			RefineLDA( app_model_path, numIters = finalIter, mustLinks = mustLinks, cannotLinks = cannotLinks, keepTerms = keepTerms, removeTerms = removeTerms )
			self.ldaDB.Reset()
			treetm_reader = TreeTMReader( self.ldaDB, app_model_path )
			treetm_reader.Execute()
			lda_computer = LDA_ComputeStats( self.ldaDB, self.corpusDB )
			lda_computer.Execute()
	
	def InspectModel(self):
		app_path = self.request.folder
		app_model_path = '{}/data/treetm'.format(app_path)
		action = self.GetAction()
		reader = InspectLDA( app_model_path )
		iterCount = reader.Iters()
		mustLinks = reader.MustLinks()
		cannotLinks = reader.CannotLinks()
		keepTerms = reader.KeepTerms()
		removeTerms = reader.RemoveTerms()
		self.content.update({
			'IterCount' : iterCount,
			'Action' : action,
			'MustLinks' : mustLinks,
			'CannotLinks' : cannotLinks,
			'KeepTerms' : keepTerms,
			'RemoveTerms' : removeTerms
		})
	
	def LoadGIB(self):
		self.LoadTopTermsPerTopic()
		self.LoadTopicCovariance()
		self.CreateTempVocabTable()
		self.LoadTermPMI()
#		self.LoadSentencePMI()
		self.DeleteTempVocabTable()

################################################################################

	def GetTermLimit(self):
		termLimit = self.GetNonNegativeIntegerParam('termLimit')
		self.params.update({
			'termLimit' : termLimit
		})
		if termLimit is None:
			termLimit = 5
		return termLimit

	def LoadTopTermsPerTopic( self ):
		termLimit = self.GetTermLimit()
		topicCount = self.db(self.db.topics).count()
		data = []
		self.vocab = set()
		for topicIndex in range(topicCount):
			query = """SELECT matrix.value AS value, terms.term_text AS term
			FROM {MATRIX} AS matrix
			INNER JOIN {TERMS} AS terms ON matrix.term_index = terms.term_index
			WHERE matrix.topic_index = {TOPIC_INDEX}
			ORDER BY matrix.rank
			LIMIT {LIMIT}""".format(MATRIX=self.db.term_topic_matrix, TERMS=self.db.terms, LIMIT=termLimit, TOPIC_INDEX=topicIndex)
			rows = self.db.executesql(query, as_dict = True)
			data.append(rows)
			self.vocab.update(row['term'] for row in rows)
		self.content.update({
			'TopTermsPerTopic' : data,
			'TopicCount' : topicCount
		})

	def LoadTopicCovariance( self ):
		query = """SELECT first_topic_index AS source, second_topic_index AS target, value
		FROM {MATRIX} AS matrix
		WHERE source != target""".format(MATRIX=self.db.topic_covariance)
		rows = self.db.executesql(query, as_dict=True)
		for index, row in enumerate(rows):
			row['rank'] = index+1
		self.content.update({
			'TopicCovariance' : rows
		})
	
	def CreateTempVocabTable( self ):
		self.bow.executesql( 'DELETE FROM vocab;' )
		self.bow.executesql( 'DELETE FROM vocab_text;' )
		self.bow.vocab_text.bulk_insert( { 'term_text' : d } for d in self.vocab )
		query = """INSERT INTO {TARGET} (term_index, term_text)
			SELECT terms.term_index, terms.term_text
			FROM {TERMS} AS terms
			INNER JOIN {SOURCE} AS vocab ON terms.term_text = vocab.term_text""".format(
				TERMS=self.bow.term_texts, SOURCE=self.bow.vocab_text, TARGET=self.bow.vocab)
		self.bow.executesql(query)
	
	def DeleteTempVocabTable( self ):
		pass

	def GetMarginalProbs( self, table ):
		query = """SELECT probs.term_index AS term_index, probs.value AS term_prob
		FROM {PROBS} AS probs
		INNER JOIN {VOCAB} AS vocab ON probs.term_index = vocab.term_index
		WHERE term_prob > 0""".format(PROBS = table, VOCAB = self.bow.vocab)
		rows = self.bow.executesql( query, as_dict = True )
		probs = { row['term_index'] : row['term_prob'] for row in rows }
		return probs
	
	def GetSparseJointProbs( self, table ):
		query = """SELECT ref1.term_text AS source, ref2.term_text AS target, matrix.first_term_index AS source_index, matrix.second_term_index AS target_index, matrix.value AS value
		FROM {MATRIX} AS matrix
		INNER JOIN {VOCAB} AS ref1 ON matrix.first_term_index = ref1.term_index
		INNER JOIN {VOCAB} AS ref2 ON matrix.second_term_index = ref2.term_index
		ORDER BY matrix.rank
		LIMIT 2000""".format(MATRIX = table, VOCAB = self.bow.vocab)
		rows = self.bow.executesql( query, as_dict = True )
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
		marginals = self.GetMarginalProbs( self.bow.term_probs )
		joints = self.GetSparseJointProbs( self.bow.term_co_probs )
		rows = self.ComputePMI( marginals, joints )
		self.content.update({
			'TermPMI' : rows
		})

	def LoadSentencePMI(self):
		marginals = self.GetMarginalProbs( self.bow.term_probs )
		joints = self.GetSparseJointProbs( self.bow.sentences_co_probs )
		rows = self.ComputePMI( marginals, joints )
		self.content.update({
			'SentencePMI' : rows
		})
