#!/usr/bin/env python

import os
import subprocess

class MalletLDA(object):
	def __init__( self, corpusPath, modelPath = 'data', tokenRegex = '\p{Alpha}{3,}', numTopics = 20, numIters = 1000, MALLET_PATH = 'tools/mallet' ):
		self.MALLET_PATH = MALLET_PATH
		self.corpusPath = corpusPath
		self.modelPath = modelPath
		self.tokenRegex = tokenRegex
		self.numTopics = numTopics
		self.numIters = numIters
		self.corpusInMallet = '{}/corpus.mallet'.format( self.modelPath )
		self.outputModel = '{}/output.model'.format( self.modelPath )
		self.outputTopicKeys = '{}/output-topic-keys.txt'.format( self.modelPath )
		self.outputTopicWordWeights = '{}/topic-word-weights.txt'.format( self.modelPath )
		self.outputDocTopicMixtures = '{}/doc-topic-mixtures.txt'.format( self.modelPath )
		self.outputWordTopicCounts = '{}/word-topic-counts.txt'.format( self.modelPath )

	def CreateModelPath( self ):
		if not os.path.exists( self.modelPath ):
			print 'Creating model folder: {}'.format( self.modelPath )
			os.makedirs( self.modelPath )

	def ImportFileOrFolder( self ):
		mallet_executable = '{}/bin/mallet'.format( self.MALLET_PATH )
		if os.path.isdir( self.corpusPath ):
			print 'Importing a folder into MALLET: [{}] --> [{}]'.format( self.corpusPath, self.corpusInMallet ) 
			command = [ mallet_executable, 'import-dir' ]
		else:
			print 'Importing a file into MALLET: [{}] --> [{}]'.format( self.corpusPath, self.corpusInMallet )
			command = [ mallet_executable, 'import-file' ]
		command += [
			'--input', self.corpusPath,
			'--output', self.corpusInMallet,
			'--remove-stopwords',
			'--token-regex', self.tokenRegex,
			'--keep-sequence'
		]
		process = subprocess.call( command )
	
	def TrainTopics( self ):
		mallet_executable = '{}/bin/mallet'.format( self.MALLET_PATH )
		print 'Training an LDA model in MALLET: [{}] --> [{}]'.format( self.corpusInMallet, self.outputModel )
		command = [
			mallet_executable, 'train-topics',
			'--input', self.corpusInMallet,
			'--output-model', self.outputModel,
			'--output-topic-keys', self.outputTopicKeys,
			'--topic-word-weights-file', self.outputTopicWordWeights,
			'--output-doc-topics', self.outputDocTopicMixtures,
			'--word-topic-counts-file', self.outputWordTopicCounts,
			'--num-topics', str(self.numTopics),
			'--num-iterations', str(self.numIters)
		]
		process = subprocess.call( command )
		
	def Execute( self ):
		self.CreateModelPath()
		self.ImportFileOrFolder()
		self.TrainTopics()
