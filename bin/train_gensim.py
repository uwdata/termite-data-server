#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import argparse
from topic_models.GensimLDA import GensimLDA

class TrainGensim( object ):
	def __init__( self ):
		pass

	def Execute( self, corpus_path, model_path, num_topics, num_passes ):
		if not os.path.exists( model_path ):
			print '--------------------------------------------------------------------------------'
			print 'Training a gensim topic model...'
			print '      corpus = {}'.format( corpus_path )
			print '       model = {}'.format( model_path )
			print '  num_topics = {}'.format( num_topics )
			print '  num_passes = {}'.format( num_passes )
			print '--------------------------------------------------------------------------------'
			gensim = GensimLDA( corpus_path, modelPath = model_path, numTopics = num_topics, numPasses = num_passes )
			gensim.Execute()
			print '--------------------------------------------------------------------------------'
		else:
			print '    Already available: {}'.format( model_path )

def main():
	parser = argparse.ArgumentParser( description = 'Train a gensim topic model.' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input text corpus'              )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model'                   )
	parser.add_argument( '--topics'     , type = int , help = 'Number of topics', default = 20 )
	parser.add_argument( '--passes'     , type = int , help = 'Training passes' , default = 1  )
	args = parser.parse_args()
	train = TrainGensim()
	train.Execute( args.corpus_path, args.model_path, args.topics, args.passes )

if __name__ == '__main__':
	main()
