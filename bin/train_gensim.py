#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import re
from gensim import corpora, models

WEB2PY_ROOT = 'tools/web2py'
DICTIONARY_FILENAME = 'corpus.dict'
MODEL_FILENAME = 'output.model'

class TrainGensim( object ):
	
	def __init__( self, corpus_path, model_path, logging_level ):
		self.corpus_path = corpus_path
		self.model_path = model_path
		self.logger = logging.getLogger( 'TrainGensim' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def execute( self, numTopics ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Training a gensim topic model...'                                                 )
		self.logger.info( '      corpus = %s', self.corpus_path                                              )
		self.logger.info( '       model = %s', self.model_path                                               )
		self.logger.info( '--------------------------------------------------------------------------------' )
		
		if not os.path.exists( self.model_path ):
			self.logger.info( 'Creating model folder: %s', self.model_path )
			os.makedirs( self.model_path )
		
		# Based on example code provided by Samuel Rönnqvist
		whitespaces = re.compile( r'\W+' )
		documents = []
		with open( self.corpus_path ) as f:
			for line in f:
				tokens = whitespaces.split( line[:-1] )
				documents.append( tokens )

		# Generate gensim dictionary
		dictionary = corpora.Dictionary( documents )
		corpus = [ dictionary.doc2bow( tokens ) for tokens in documents ]
		model = models.LdaModel( corpus, id2word = dictionary, num_topics = numTopics )
		
		filename = '{}/{}'.format( self.model_path, DICTIONARY_FILENAME )
		self.logger.info( 'Saving dictionary to disk: %s', filename )
		dictionary.save( filename )
		
		filename = '{}/{}'.format( self.model_path, MODEL_FILENAME )
		self.logger.info( 'Saving model to disk: %s', filename )
		model.save( filename )

def main():
	parser = argparse.ArgumentParser( description = 'Train a gensim topic model.' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input text corpus'                            )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model'                                 )
	parser.add_argument( '--topics'     , type = int , help = 'Number of topics'     , default = 20          )
	parser.add_argument( '--logging'    , type = int , help = 'Override default logging level', default = 20 )
	args = parser.parse_args()
	
	TrainGensim(
		corpus_path = args.corpus_path,
		model_path = args.model_path,
		logging_level = args.logging
	).execute(
		numTopics = args.topics,
	)

if __name__ == '__main__':
	main()
