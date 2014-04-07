#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import argparse
from topic_models.MalletLDA import MalletLDA

class TrainMallet(object):
	def __init__( self ):
		pass

	def Execute( self, corpus_path, model_path, token_regex, num_topics, num_iters ):
		if not os.path.exists( model_path ):
			print '--------------------------------------------------------------------------------'
			print 'Training an LDA topic model...'
			print '      corpus = {}'.format( corpus_path )
			print '       model = {}'.format( model_path )
			print ' token_regex = {}'.format( token_regex )
			print '  num_topics = {}'.format( num_topics )
			print '   num_iters = {}'.format( num_iters )
			print '--------------------------------------------------------------------------------'
			lda = MalletLDA( corpus_path, modelPath = model_path, tokenRegex = token_regex, numTopics = num_topics, numIters = num_iters )
			lda.Execute()
			print '--------------------------------------------------------------------------------'
		else:
			print '    Already available: {}'.format( model_path )


def main():
	parser = argparse.ArgumentParser( description = 'Train an LDA topic model using MALLET.' )
	parser.add_argument( 'corpus_path', type = str , help = 'Input text corpus as a folder or a file' )
	parser.add_argument( 'model_path' , type = str , help = 'Output model path'                       )
	parser.add_argument( '--topics'     , dest = 'topics'     , type = int , help = 'Number of topics'    , default = 20              )
	parser.add_argument( '--iters'      , dest = 'iters'      , type = int , help = 'Number of iterations', default = 1000            )
	parser.add_argument( '--token-regex', dest = 'token_regex', type = str , help = 'Tokenization'        , default = '\p{Alpha}{3,}' )
	args = parser.parse_args()
	train = TrainMallet()
	train.Execute( args.corpus_path, args.model_path, args.token_regex, args.topics, args.iters )

if __name__ == '__main__':
	main()
