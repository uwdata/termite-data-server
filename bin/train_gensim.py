#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import argparse
import re
from gensim import corpora, models

DICTIONARY_FILENAME = 'corpus.dict'
MODEL_FILENAME = 'output.model'

WHITESPACES = re.compile( r'\W+' )
LINEBREAKS = re.compile( r'[\t\n\x0B\f\r]+' )

class TrainGensim( object ):
	
	def __init__( self ):
		pass
	
	def Execute( self, corpus_path, model_path, num_topics ):
		print '--------------------------------------------------------------------------------'
		print 'Training a gensim topic model...'
		print '      corpus = {}'.format( corpus_path )
		print '       model = {}'.format( model_path )
		print '  num_topics = {}'.format( num_topics )
		print '--------------------------------------------------------------------------------'
		
		if not os.path.exists( model_path ):
			print 'Creating model folder: {}'.format( model_path )
			os.makedirs( model_path )
		
		# Based on example code provided by Samuel Rönnqvist
		documents = []
		if os.path.isdir( corpus_path ):
			# Read two levels of files
			filenames = []
			filenames += glob.glob( '{}/*'.format( corpus_path ) )
			for filename in filenames:
				if os.path.isdir( filename ):
					filenames += glob.glob( '{}/*'.format( filename ) )
			for filename in filenames:
				if not os.path.isdir( filename ):
					with open( filename ) as f:
						tokens = WHITESPACES.split( LINEBREAKS.sub( ' ', f.read().decode( 'utf-8', 'ignore' ) ) )
						documents.append( tokens )
		else:
			with open( corpus_path ) as f:
				for line in f:
					tokens = WHITESPACES.split( line[:-1].decode( 'utf-8', 'ignore' ) )
					documents.append( tokens )

		# Generate gensim dictionary
		dictionary = corpora.Dictionary( documents )
		corpus = [ dictionary.doc2bow( tokens ) for tokens in documents ]
		model = models.LdaModel( corpus, id2word = dictionary, num_topics = num_topics )
		
		filename = '{}/{}'.format( model_path, DICTIONARY_FILENAME )
		print 'Saving dictionary to disk: {}'.format( filename )
		dictionary.save( filename )
		
		filename = '{}/{}'.format( model_path, MODEL_FILENAME )
		print 'Saving model to disk: {}'.format( filename )
		model.save( filename )

def main():
	parser = argparse.ArgumentParser( description = 'Train a gensim topic model.' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input text corpus'              )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model'                   )
	parser.add_argument( '--topics'     , type = int , help = 'Number of topics', default = 20 )
	args = parser.parse_args()
	
	train = TrainGensim()
	train.Execute( args.corpus_path, args.model_path, args.topics )

if __name__ == '__main__':
	main()
