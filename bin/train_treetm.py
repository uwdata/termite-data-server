#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
from modellers.TreeTM import BuildLDA, RefineLDA, InspectLDA

def TrainTreeTM( corpus_path, model_path, token_regex, num_topics, num_iters, is_quiet, force_overwrite, resume_training, inspect_only ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	corpus_filename = '{}/corpus.txt'.format(corpus_path)
	if force_overwrite or not os.path.exists( model_path ):
		logger.info( '--------------------------------------------------------------------------------' )
		logger.info( 'Training a new interactive topic model...' )
		logger.info( '       corpus = %s', corpus_filename )
		logger.info( '        model = %s', model_path )
		logger.info( '  token_regex = %s', token_regex )
		logger.info( '       topics = %s', num_topics )
		logger.info( '        iters = %s', num_iters )
		logger.info( '--------------------------------------------------------------------------------' )
		BuildLDA( corpus_filename, model_path, tokenRegex = token_regex, numTopics = num_topics, numIters = num_iters )
	else:
		if inspect_only:
			logger.info( '--------------------------------------------------------------------------------' )
			logger.info( 'Inspecting an existing interactive topic model...' )
			logger.info( '    model = %s', model_path )
			logger.info( '--------------------------------------------------------------------------------' )
			reader = InspectLDA( model_path )
			logger.info( 'Entry' )
			logger.info( reader.EntryID() )
			logger.info( 'Iters' )
			logger.info( reader.Iters() )
			logger.info( 'MustLinks' )
			logger.info( json.dumps(reader.MustLinks(), encoding='utf-8', indent=2))
			logger.info( 'CannotLinks' )
			logger.info( json.dumps(reader.CannotLinks(), encoding='utf-8', indent=2))
			logger.info( 'KeepTerms' )
			logger.info( json.dumps(reader.KeepTerms(), encoding='utf-8', indent=2))
			logger.info( 'RemoveTerms' )
			logger.info( json.dumps(reader.RemoveTerms(), encoding='utf-8', indent=2))
		elif resume_training:
			logger.info( '--------------------------------------------------------------------------------' )
			logger.info( 'Training an existing interactive topic model...' )
			logger.info( '    model = %s', model_path )
			logger.info( '    iters = %s', num_iters )
			logger.info( '--------------------------------------------------------------------------------' )
			RefineLDA( model_path, numIters = num_iters )
		else:
			logger.info( '--------------------------------------------------------------------------------' )
			logger.info( 'Training an interactive topic model...' )
			logger.info( '--------------------------------------------------------------------------------' )
			logger.info( '    Already exists: %s', model_path )

def main():
	parser = argparse.ArgumentParser( description = 'Train an interactive topic model.' )
	parser.add_argument( 'corpus_path'  , type = str                         , help = 'Input folder containing the text corpus as "corpus.txt"' )
	parser.add_argument( 'model_path'   , type = str                         , help = 'Output model folder' )
	parser.add_argument( '--token-regex', type = str   , default = r'\w{3,}' , help = 'Tokenization', dest = 'token_regex' )
	parser.add_argument( '--topics'     , type = int   , default = 20        , help = 'Number of topics' )
	parser.add_argument( '--iters'      , type = int   , default = 1000      , help = 'Number of iterations' )
	parser.add_argument( '--quiet'      , const = True , default = False     , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False     , help = 'Overwrite any existing model', action = 'store_const' )
	parser.add_argument( '--resume'     , const = True , default = False     , help = 'Resume training', action = 'store_const' )
	parser.add_argument( '--read-only'  , const = True , default = False     , help = 'Retrieve a previous model without training', action = 'store_const', dest = 'read_only' )
	args = parser.parse_args()
	TrainTreeTM( args.corpus_path, args.model_path, args.token_regex, args.topics, args.iters, args.quiet, args.overwrite, args.resume, args.read_only )

if __name__ == '__main__':
	main()
