#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging

def TrainSTM( is_quiet, overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	logger.info( 'STM models currently need to be trained in R.' )
	logger.info( 'Please genreate an RData file where the model output is saved as variable "mod.out".' )

def main():
	parser = argparse.ArgumentParser( description = 'Train a structural topic model.' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input text corpus (as a folder or a file)' )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model path' )
	args = parser.parse_args()
	TrainSTM( False, False )

if __name__ == '__main__':
	main()
