#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from gensim import corpora, models

class GensimReader():
	DICTIONARY_FILENAME = 'dictionary.gensim'
	CORPUS_FILENAME = 'corpus.gensim'
	MODEL_FILENAME = 'lda.gensim'

	def __init__( self, modelPath, LDA_DB ):
		self.logger = logging.getLogger('termite')
		self.modelPath = modelPath
		self.dictionaryInGensim = '{}/{}'.format( self.modelPath, GensimReader.DICTIONARY_FILENAME )
		self.corpusInGensim = '{}/{}'.format( self.modelPath, GensimReader.CORPUS_FILENAME )
		self.modelInGensim = '{}/{}'.format( self.modelPath, GensimReader.MODEL_FILENAME )
		self.ldaDB = LDA_DB
		
	def Execute( self ):
		self.ReadDictionaryAndModel()
		self.SaveToDB()
	
	def ReadDictionaryAndModel( self ):
		self.logger.info( 'Reading dictionary from: %s', self.dictionaryInGensim )
		self.dictionary = corpora.Dictionary.load( self.dictionaryInGensim )
		self.logger.info( 'Reading corpus from: %s', self.corpusInGensim )
		self.corpus = corpora.TextCorpus.load( self.corpusInGensim )
		self.logger.info( 'Reading model from: %s', self.modelInGensim )
		self.model = models.LdaModel.load( self.modelInGensim )
	
	def SaveToDB( self ):
		topicsAndFreqsTerms = self.model.show_topics( topics = -1, topn = len(self.dictionary), formatted = False )
		docsAndFreqsTopics = self.corpus

		termTable = []
		docTable = []
		topicTable = []
		termLookup = {}
		for index in self.dictionary:
			term = self.dictionary[index]
			termTable.append({
				'term_index' : index,
				'text' : term
			})
			termLookup[term] = index
		for doc, _ in enumerate(docsAndFreqsTopics):
			docTable.append({
				'doc_index' : doc
			})
		for topic, freqsTerms in enumerate(topicsAndFreqsTerms):
			topicTable.append({
				'topic_index' : topic,
				'freq' : sum( freq for freq, term in freqsTerms ),
				'desc' : u', '.join( term for freq, term in freqsTerms[:5] ),
				'top_terms' : [ term for freq, term in freqsTerms[:20] ]
			})
		termIndexes = self.ldaDB.db.terms.bulk_insert(termTable)
		docIndexes = self.ldaDB.db.docs.bulk_insert(docTable)
		topicIndexes = self.ldaDB.db.topics.bulk_insert(topicTable)

		termTopicMatrix = []
		docTopicMatrix = []
		for topic, freqsTerms in enumerate(topicsAndFreqsTerms):
			for freq, term in freqsTerms:
				termTopicMatrix.append({
					'term_index' : termLookup[term],
				 	'topic_index' : topic,
					'value' : freq
				})
		for docIndex, freqsTopics in enumerate(docsAndFreqsTopics):
			for freq, topic in freqsTopics:
				docTopicMatrix.append({
					'doc_index' : docIndex,
					'topic_index' : topic,
					'value' : freq
				})
		termTopicMatrix.sort( key = lambda x : -x['value'] )
		docTopicMatrix.sort( key = lambda x : -x['value'] )
		self.ldaDB.db.term_topic_matrix.bulk_insert(termTopicMatrix)
		self.ldaDB.db.doc_topic_matrix.bulk_insert(docTopicMatrix)
