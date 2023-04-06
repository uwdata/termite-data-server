#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from gensim import corpora, models
from .LDAReader import LDAReader

class GensimReader(LDAReader):
	"""
	lda_db = a SQLite3 database
	modelPath = a model folder containing files dictionary.gensim, corpus.gensim, and lda.gensim
	"""
	
	DICTIONARY_FILENAME = 'dictionary.gensim'
	CORPUS_FILENAME = 'corpus.gensim'
	MODEL_FILENAME = 'lda.gensim'
	STATE_FILENAME = 'state.gensim'

	def __init__( self, lda_db, modelPath, corpus_db, extraStateFile = False ):
		super(GensimReader, self).__init__(lda_db)
		self.modelPath = modelPath
		self.dictionaryInGensim = '{}/{}'.format( self.modelPath, GensimReader.DICTIONARY_FILENAME )
		self.corpusInGensim = '{}/{}'.format( self.modelPath, GensimReader.CORPUS_FILENAME ) if corpus_db is not None else None 
		self.modelInGensim = '{}/{}'.format( self.modelPath, GensimReader.MODEL_FILENAME )
		self.stateInGensim = '{}/{}'.format( self.modelPath, GensimReader.STATE_FILENAME ) if extraStateFile else None
		self.corpus = corpus_db.db if corpus_db is not None else None
		
	def Execute( self ):
		self.logger.info( 'Reading gensim LDA output...' )
		self.ReadDictionaryAndModel()
		self.logger.info( 'Writing to database...' )
		self.SaveToDB()
	
	def ReadDictionaryAndModel( self ):
		self.logger.debug( '    Loading dictionary: %s', self.dictionaryInGensim )
		self.dictionary = corpora.Dictionary.load( self.dictionaryInGensim )
		self.logger.debug( '    Loading corpus: %s', self.corpusInGensim )
		self.text_corpus = corpora.TextCorpus.load( self.corpusInGensim ) if self.corpus is not None else None 
		self.logger.debug( '    Loading model: %s', self.modelInGensim )
		self.model = models.LdaModel.load( self.modelInGensim )
		if self.stateInGensim is not None:
			self.model.state = models.ldamodel.LdaState.load( self.stateInGensim )
		
		self.termList = [ self.dictionary[index] for index in self.dictionary ]
		self.docList = [ d.doc_id for d in self.corpus().select(self.corpus.corpus.doc_id, orderby=self.corpus.corpus.doc_index) ] if self.corpus is not None else None

		self.termTopicMatrix = []
		topicsAndFreqsTerms = self.model.show_topics(topics=-1, topn=len(self.dictionary), formatted=False)
		for topicIndex, freqsTerms in enumerate(topicsAndFreqsTerms):
			for value, term in freqsTerms:
				self.termTopicMatrix.append({
					'term_index' : term,
					'topic_index' : topicIndex,
					'value' : value,
					'rank' : 0
				})
		termLookup = { term : termIndex for termIndex, term in enumerate(self.termList) }
		self.termTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.termTopicMatrix):
			d['term_index'] = termLookup[d['term_index']]
			d['rank'] = index + 1
		
		self.docTopicMatrix = []
		if self.corpus is not None:
			docsAndDocBOWs = self.text_corpus
			for docIndex, docBOW in enumerate(docsAndDocBOWs):
				topicsProbs = self.model[docBOW]
				for topicIndex, value in topicsProbs:
					self.docTopicMatrix.append({
						'doc_index' : docIndex,
						'topic_index' : topicIndex,
						'value' : value,
						'rank' : 0
					})
		self.docTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.docTopicMatrix):
			d['rank'] = index + 1
