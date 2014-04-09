#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import logging
import os
import re
from gensim import corpora, models, utils
from gensim.parsing.preprocessing import STOPWORDS

WHITESPACES = re.compile( r'\W+' )
LINEBREAKS = re.compile( r'[\t\n\x0B\f\r]+' )

def preprocess(tokens):
	"""Lowercase, remove stopwords etc. from a list of unicode strings."""
	result = [token.lower().encode('utf8') for token in tokens if len(token) > 2 and token.isalpha()]
	return [token for token in result if token not in STOPWORDS]
	
class TermiteCorpus(corpora.TextCorpus):
	def get_texts(self):
		total_docs = 0
		if os.path.isdir( self.input ):
			# Read two levels of files
			filenames = glob.glob( '{}/*'.format( self.input ) )
			for filename in filenames:
				if os.path.isdir( filename ):
					filenames += glob.glob( '{}/*'.format( filename ) )

			for filename in filenames:
				if not os.path.isdir( filename ):
					with utils.smart_open( filename ) as f:
						tokens = WHITESPACES.split( LINEBREAKS.sub( ' ', f.read().decode( 'utf-8', 'ignore' ) ).strip() )
						yield preprocess(tokens)
						total_docs += 1
		else:
			with utils.smart_open( self.input ) as f:
				for line in f:
					tokens = WHITESPACES.split( line[:-1].decode( 'utf-8', 'ignore' ) )
					yield preprocess(tokens)
					total_docs += 1
		self.length = total_docs

class GensimLDA( object ):

	DICTIONARY_FILENAME = 'corpus.dict'
	MODEL_FILENAME = 'output.model'

	def __init__( self, corpusPath, modelPath = 'data', numTopics = 20, numPasses = 1 ):
		self.logger = logging.getLogger('termite')
		
		self.corpusPath = corpusPath
		self.modelPath = modelPath
		self.numTopics = numTopics
		self.numPasses = numPasses

	def Execute( self ):
		dict_filename = '{}/{}'.format( self.modelPath, GensimLDA.DICTIONARY_FILENAME )
		model_filename = '{}/{}'.format( self.modelPath, GensimLDA.MODEL_FILENAME )

		if not os.path.exists( self.modelPath ):
			self.logger.info( 'Creating model folder: %s', self.modelPath )
			os.makedirs( self.modelPath )

		# Generate gensim objects
		corpus = TermiteCorpus( self.corpusPath )
		corpus.dictionary.filter_extremes( no_above = 0.2 )  # remove words that are too frequent/too infrequent
		model = models.LdaModel( corpus, id2word = corpus.dictionary, num_topics = self.numTopics, passes = self.numPasses )

		self.logger.info( 'Saving dictionary to disk: %s', dict_filename )
		corpus.dictionary.save( dict_filename )

		self.logger.info( 'Saving model to disk: %s', model_filename )
		model.save( model_filename )
