#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import subprocess

class MalletLDA(object):
	def __init__( self, corpusPath, modelPath = 'data', tokenRegex = '\p{Alpha}{3,}', numTopics = 20, numIters = 1000, MALLET_PATH = 'tools/mallet' ):
		self.MALLET_PATH = MALLET_PATH
		self.logger = logging.getLogger('termite')
		
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
			self.logger.info( 'Creating model folder: %s', self.modelPath )
			os.makedirs( self.modelPath )

	def ImportFileOrFolder( self ):
		mallet_executable = '{}/bin/mallet'.format( self.MALLET_PATH )
		if os.path.isdir( self.corpusPath ):
			self.logger.info( 'Importing a folder into MALLET: [%s] --> [%s]', self.corpusPath, self.corpusInMallet ) 
			command = [ mallet_executable, 'import-dir' ]
		else:
			self.logger.info( 'Importing a file into MALLET: [%s] --> [%s]', self.corpusPath, self.corpusInMallet )
			command = [ mallet_executable, 'import-file' ]
		command += [
			'--input', self.corpusPath,
			'--output', self.corpusInMallet,
			'--remove-stopwords',
			'--token-regex', self.tokenRegex,
			'--keep-sequence'
		]
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			self.logger.debug( p.stdout.readline().rstrip('\n') )
	
	def TrainTopics( self ):
		mallet_executable = '{}/bin/mallet'.format( self.MALLET_PATH )
		self.logger.info( 'Training an LDA model in MALLET: [%s] --> [%s]', self.corpusInMallet, self.outputModel )
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
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			self.logger.debug( p.stdout.readline().rstrip('\n') )
		
	def Execute( self ):
		self.CreateModelPath()
		self.ImportFileOrFolder()
		self.TrainTopics()
