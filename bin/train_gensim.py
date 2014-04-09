#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os.path
from topic_models.GensimLDA import GensimLDA

def TrainGensim( corpus_path, model_path, num_topics, num_passes, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	gensimLogger = logging.getLogger('gensim.models.ldamodel')
	gensimLogger.addHandler( logging.StreamHandler() )
	gensimLogger.setLevel( logging.WARNING if is_quiet else logging.INFO )
	
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Training an LDA topic model using gensim...' )
	logger.info( ' corpus_path = %s', corpus_path )
	logger.info( '  model_path = %s', model_path )
	logger.info( '      topics = %s', num_topics )
	logger.info( '      passes = %s', num_passes )
	logger.info( '--------------------------------------------------------------------------------' )

	if force_overwrite or not os.path.exists( model_path ):
		gensim = GensimLDA( corpus_path, modelPath = model_path, numTopics = num_topics, numPasses = num_passes )
		gensim.Execute()
	else:
		logger.info( '    Already available: %s', model_path )

	logger.info( '--------------------------------------------------------------------------------' )

def main():
	parser = argparse.ArgumentParser( description = 'Train an LDA topic model using gensim.' )
	parser.add_argument( 'corpus_path' , type = str                     , help = 'Input text corpus' )
	parser.add_argument( 'model_path'  , type = str                     , help = 'Output model' )
	parser.add_argument( '--topics'    , type = int   , default = 20    , help = 'Number of topics' )
	parser.add_argument( '--passes'    , type = int   , default = 1     , help = 'Training passes' )
	parser.add_argument( '--quiet'     , const = True , default = False , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite' , const = True , default = False , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	TrainGensim( args.corpus_path, args.model_path, args.topics, args.passes, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
