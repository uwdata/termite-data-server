#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import argparse
import re
import logging
from gensim import corpora, models, utils
from gensim.parsing.preprocessing import STOPWORDS

DICTIONARY_FILENAME = 'corpus.dict'
MODEL_FILENAME = 'output.model'

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


class TrainGensim( object ):

	def __init__( self ):
		pass

	def Execute( self, corpus_path, model_path, num_topics, num_passes ):
		print '--------------------------------------------------------------------------------'
		print 'Training a gensim topic model...'
		print '      corpus = {}'.format( corpus_path )
		print '       model = {}'.format( model_path )
		print '  num_topics = {}'.format( num_topics )
		print '  num_passes = {}'.format( num_passes )
		print '--------------------------------------------------------------------------------'

		dict_filename = '{}/{}'.format( model_path, DICTIONARY_FILENAME )
		model_filename = '{}/{}'.format( model_path, MODEL_FILENAME )

		if not os.path.exists( dict_filename ) or not os.path.exists( model_filename ):
			if not os.path.exists( model_path ):
				print 'Creating model folder: {}'.format( model_path )
				os.makedirs( model_path )

			# Generate gensim objects
			logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
			corpus = TermiteCorpus( corpus_path )
			corpus.dictionary.filter_extremes( no_above = 0.2 )  # remove words that are too frequent/too infrequent
			model = models.LdaModel( corpus, id2word = corpus.dictionary, num_topics = num_topics, passes = num_passes )

			print 'Saving dictionary to disk: {}'.format( dict_filename )
			corpus.dictionary.save( dict_filename )

			print 'Saving model to disk: {}'.format( model_filename )
			model.save( model_filename )
		
		else:
			print 'Already available: {}'.format( model_path )

		print '--------------------------------------------------------------------------------'

def main():
	parser = argparse.ArgumentParser( description = 'Train a gensim topic model.' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input text corpus'              )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model'                   )
	parser.add_argument( '--topics'     , type = int , help = 'Number of topics', default = 20 )
	parser.add_argument( '--passes'     , type = int , help = 'Training passes', default = 1 )
	args = parser.parse_args()

	train = TrainGensim()
	train.Execute( args.corpus_path, args.model_path, args.topics, args.passes )

if __name__ == '__main__':
	main()
