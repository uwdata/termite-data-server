#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import argparse
from topic_models.LDA import LDA

class TrainMallet(object):

	def __init__( self, mallet_path = 'tools/mallet' ):
		self.MALLET_PATH = mallet_path
	
	def Execute( self, corpus_path, model_path, num_topics, num_iters, token_regex ):
		if not os.path.exists( model_path ):
			print '--------------------------------------------------------------------------------'
			print 'Training an LDA topic model...'
			print '      corpus = {}'.format( corpus_path )
			print '       model = {}'.format( model_path )
			print '  num_topics = {}'.format( num_topics )
			print '   num_iters = {}'.format( num_iters )
			print ' token_regex = {}'.format( token_regex )
			print '--------------------------------------------------------------------------------'

			if not os.path.exists( model_path ):
				print 'Creating model folder: {}'.format( model_path )
				os.makedirs( model_path )
			mallet_executable = '{}/bin/mallet'.format( self.MALLET_PATH )
			model_filename = '{}/corpus.mallet'.format( model_path )
			
			if os.path.isdir( corpus_path ):
				print 'Importing a folder into MALLET: [{}] --> [{}]'.format(corpus_path, model_filename)
				command = [ mallet_executable, 'import-dir' ]
			else:
				print 'Importing a file into MALLET: [{}] --> [{}]'.format(corpus_path, model_filename)
				command = [ mallet_executable, 'import-file' ]
			command += [ '--input', corpus_path ]
			command += [ '--output', model_filename ]
			command += [ '--remove-stopwords' ]
			command += [ '--token-regex', token_regex ]
			command += [ '--keep-sequence' ]
			process = subprocess.call( command )
			
			print 'Training an LDA topic model: [{}]'.format(model_path)
			lda = LDA( malletPath = self.MALLET_PATH, modelPath = model_path, numTopics = num_topics, numIters = num_iters )
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
	train.Execute( args.corpus_path, args.model_path, args.topics, args.iters, args.token_regex )

if __name__ == '__main__':
	main()
