#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import shutil

def TrainSTM( corpus_path, model_path, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	source_filename = '{}/stm.RData'.format(corpus_path)
	target_filename = '{}/stm.RData'.format(model_path)
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Copying pre-computed STM models (saved as RData with variable "mod.out")' )
	logger.info( '    corpus = %s', corpus_path )
	logger.info( '     model = %s', model_path )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists(target_filename):
		if not os.path.exists(model_path):
			os.makedirs(model_path)
		logger.info( '    Copying [%s] --> [%s]', source_filename, target_filename )
		shutil.copy(source_filename, target_filename)
	else:
		logger.info( '    Already exists: %s', model_path )

def main():
	parser = argparse.ArgumentParser( description = 'Train a structural topic model.' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input folder containing the text corpus as "corpus.txt"' )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model folder' )
	parser.add_argument( '--quiet'      , const = True , default = False, help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False, help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	TrainSTM( args.corpus_path, args.model_path, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
