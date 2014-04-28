#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
from modellers.MalletLDA import BuildMultipleLDAs

def TrainMalletN( corpus_path, model_path, token_regex, num_topics, num_iters, num_models, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	corpus_filename = '{}/corpus.txt'.format(corpus_path)
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Training an LDA topic model using MALLET...' )
	logger.info( '       corpus = %s', corpus_filename )
	logger.info( '        model = %s', model_path )
	logger.info( '  token_regex = %s', token_regex )
	logger.info( '       topics = %s', num_topics )
	logger.info( '        iters = %s', num_iters )
	logger.info( '       models = %s', num_models )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists( model_path ):
		BuildMultipleLDAs( corpus_filename, model_path, tokenRegex = token_regex, numTopics = num_topics, numIters = num_iters, numModels = num_models )
	else:
		logger.info( '    Already exists: %s', model_path )

def main():
	parser = argparse.ArgumentParser( description = 'Train an LDA topic model using MALLET.' )
	parser.add_argument( 'corpus_path'  , type = str                         , help = 'Input folder containing the text corpus as "corpus.txt"' )
	parser.add_argument( 'model_path'   , type = str                         , help = 'Output model folder' )
	parser.add_argument( '--token-regex', type = str   , default = r'\w{3,}' , help = 'Tokenization', dest = 'token_regex' )
	parser.add_argument( '--topics'     , type = int   , default = 20        , help = 'Number of topics' )
	parser.add_argument( '--iters'      , type = int   , default = 1000      , help = 'Number of iterations' )
	parser.add_argument( '--models'     , type = int   , default = 50        , help = 'Number of models' )
	parser.add_argument( '--quiet'      , const = True , default = False     , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False     , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	TrainMalletN( args.corpus_path, args.model_path, args.token_regex, args.topics, args.iters, args.models, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
