#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
from CommonLDA import CommonLDA
from gensim import corpora, models

class GensimLDA( CommonLDA ):

	DICTIONARY_FILENAME = 'corpus.dict'
	MODEL_FILENAME = 'output.model'

	def __init__( self, app_path, model_path ):
		self.logger = logging.getLogger('termite')

		self.app_path = app_path
		self.data_path = '{}/data/lda'.format( self.app_path )
		self.model_path = model_path
		self.filenameDictionary = '{}/{}'.format( self.model_path, GensimLDA.DICTIONARY_FILENAME )
		self.filenameModel = '{}/{}'.format( self.model_path, GensimLDA.MODEL_FILENAME )
	
	def Exists( self ):
		return os.path.exists( self.data_path )
		
	def Execute( self ):
		if not os.path.exists( self.data_path ):
			os.makedirs( self.data_path )
		self.ReadDictionaryAndModel()
		self.SaveToDisk()
		self.TransposeMatrices()
		self.ComputeTopicCooccurrenceAndCovariance()
	
	def ReadDictionaryAndModel( self ):
		self.logger.info( 'Reading dictionary from: %s', self.filenameDictionary )
		self.dictionary = corpora.Dictionary.load( self.filenameDictionary )
		self.logger.info( 'Reading model from: %s', self.filenameModel )
		self.model = models.LdaModel.load( self.filenameModel )
	
	def SaveToDisk( self ):
		termTexts = {}
		for i in self.dictionary:
			termTexts[i] = self.dictionary[i]
		topics = self.model.show_topics( topics = -1, topn = len(termTexts), formatted = False )

		docIndex = []
		termIndex = [ None ] * len( termTexts )
		topicIndex = [ None ] * len( topics )
		termsAndTopics = {}
		docsAndTopics = {}

		for termID, termText in termTexts.iteritems():
			termIndex[termID] = {
				'index' : termID,
				'text' : termText,
				'docFreq' : self.dictionary.dfs[termID]
			}
			termsAndTopics[ termText ] = [ 0.0 ] * len( topics )
		for n, topic in enumerate( topics ):
			topicIndex[n] = {
				'index' : n
			}
			for freq, termText in topic:
				termsAndTopics[ termText ][ n ] = freq
	
		self.logger.info( 'Writing data to disk: %s', self.data_path )
		filename = '{}/doc-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-topic-matrix.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( docsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
