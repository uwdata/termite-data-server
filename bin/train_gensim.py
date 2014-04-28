#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
from modellers.GensimLDA import BuildLDA

def TrainGensim( corpus_path, model_path, token_regex, num_topics, num_passes, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	gensimLogger = logging.getLogger('gensim.models.ldamodel')
	gensimLogger.addHandler( logging.StreamHandler() )
	gensimLogger.setLevel( logging.WARNING if is_quiet else logging.INFO )
	
	corpus_filename = '{}/corpus.txt'.format(corpus_path)
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Training an LDA topic model using gensim...' )
	logger.info( '       corpus = %s', corpus_filename )
	logger.info( '        model = %s', model_path )
	logger.info( '  token_regex = %s', token_regex )
	logger.info( '       topics = %s', num_topics )
	logger.info( '       passes = %s', num_passes )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists( model_path ):
		BuildLDA( corpus_filename, modelPath = model_path, tokenRegex = token_regex, numTopics = num_topics, numPasses = num_passes )
	else:
		logger.info( '    Already exists: %s', model_path )

def main():
	parser = argparse.ArgumentParser( description = 'Train an LDA topic model using gensim.' )
	parser.add_argument( 'corpus_path'  , type = str                         , help = 'Input folder containing the text corpus as "corpus.txt"' )
	parser.add_argument( 'model_path'   , type = str                         , help = 'Output model folder' )
	parser.add_argument( '--token-regex', type = str   , default = r'\w{3,}' , help = 'Tokenization', dest = 'token_regex' )
	parser.add_argument( '--topics'     , type = int   , default = 20        , help = 'Number of topics' )
	parser.add_argument( '--passes'     , type = int   , default = 1         , help = 'Training passes' )
	parser.add_argument( '--quiet'      , const = True , default = False     , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False     , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	TrainGensim( args.corpus_path, args.model_path, args.token_regex, args.topics, args.passes, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
