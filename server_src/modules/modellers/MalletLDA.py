#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import subprocess

class BuildMultipleLDAs(object):
	"""
	corpusPath = A single tab-delimited file containing the corpus (one document per line, two columns containing docID and docContent, without headers)
	modelPath = Folder for storing all output files
	numModels = Number of models
	tokenRegex, numTopics, numIters = Other parameters
	"""
	def __init__( self, corpusPath, modelPath, numModels = 50, tokenRegex = r'\w{3,}', numTopics = 20, numIters = 1000, MALLET_PATH = 'tools/mallet' ):
		with ImportMalletCorpus( corpusPath, modelPath ) as importer:
			importer.ImportFileOrFolder( tokenRegex )
		for index in range( numModels ):
			modelSubPath = '{}/model_{:03d}'.format( modelPath, index )
			with TrainMalletLDA( modelPath, modelSubPath ) as builder:
				builder.TrainTopics( numTopics, numIters )

class BuildLDA(object):
	"""
	corpusPath = A single tab-delimited file containing the corpus (one document per line, two columns containing docID and docContent, without headers)
	modelPath = Folder for storing all output files
	tokenRegex, numTopics, numIters = Other parameters
	"""
	def __init__( self, corpusPath, modelPath, tokenRegex = r'\w{3,}', numTopics = 20, numIters = 1000, MALLET_PATH = 'tools/mallet' ):
		with ImportMalletCorpus( corpusPath, modelPath ) as importer:
			importer.ImportFileOrFolder( tokenRegex )
		with TrainMalletLDA( modelPath, modelPath ) as builder:
			builder.TrainTopics( numTopics, numIters )

class ImportMalletCorpus(object):
	def __init__( self, inputPath, corpusPath, MALLET_PATH = 'tools/mallet' ):
		self.logger = logging.getLogger('termite')
		self.malletExecutable =  '{}/bin/mallet'.format( MALLET_PATH )
		self.inputPath = inputPath
		self.corpusPath = corpusPath
		self.corpusInMallet = '{}/corpus.mallet'.format( self.corpusPath )

	def Shell( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )
	
	def __enter__( self ):
		return self
	
	def __exit__( self, type, value, traceback ):
		pass

	def ImportFileOrFolder( self, tokenRegex = None, removeStopwords = True, stoplistFile = None, keepSequence = True ):
		if not os.path.exists( self.corpusPath ):
			os.makedirs( self.corpusPath )

		if os.path.isdir( self.inputPath ):
			self.logger.info( 'Importing a folder into MALLET: [%s] --> [%s]', self.inputPath, self.corpusInMallet ) 
			command = [ self.malletExecutable, 'import-dir' ]
		else:
			self.logger.info( 'Importing a file into MALLET: [%s] --> [%s]', self.inputPath, self.corpusInMallet )
			command = [ self.malletExecutable, 'import-file' ]
		command += [ '--input', self.inputPath ]
		command += [ '--output', self.corpusInMallet ]
		if removeStopwords:
			command += [ '--remove-stopwords' ]
		if stoplistFile is not None:
			command += [ '--stoplist-file', stoplistFile ]
		if tokenRegex is not None:
			command += [ '--token-regex', tokenRegex ]
		if keepSequence:
			command += [ '--keep-sequence' ]
		self.Shell( command )
	
class TrainMalletLDA(object):
	def __init__( self, corpusPath, modelPath, MALLET_PATH = 'tools/mallet' ):
		self.logger = logging.getLogger('termite')
		self.malletExecutable =  '{}/bin/mallet'.format( MALLET_PATH )
		self.corpusPath = corpusPath
		self.corpusInMallet = '{}/corpus.mallet'.format( self.corpusPath )
		self.modelPath = modelPath
		self.outputModel = '{}/lda.mallet'.format( self.modelPath )
		self.outputTopicKeys = '{}/output-topic-keys.txt'.format( self.modelPath )
		self.outputTopicWordWeights = '{}/topic-word-weights.txt'.format( self.modelPath )
		self.outputDocTopicMixtures = '{}/doc-topic-mixtures.txt'.format( self.modelPath )
		self.outputWordTopicCounts = '{}/word-topic-counts.txt'.format( self.modelPath )

	def Shell( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )

	def __enter__( self ):
		return self

	def __exit__( self, type, value, traceback ):
		pass

	def TrainTopics( self, numTopics = None, numIters = None ):
		if not os.path.exists( self.modelPath ):
			os.makedirs( self.modelPath )

		self.logger.info( 'Training an LDA model in MALLET: [%s] --> [%s]', self.corpusInMallet, self.outputModel )
		command = [
			self.malletExecutable, 'train-topics',
			'--input', self.corpusInMallet,
			'--output-model', self.outputModel,
			'--output-topic-keys', self.outputTopicKeys,
			'--topic-word-weights-file', self.outputTopicWordWeights,
			'--output-doc-topics', self.outputDocTopicMixtures,
			'--word-topic-counts-file', self.outputWordTopicCounts
		]
		if numTopics is not None:
			command += [ '--num-topics', str(numTopics) ]
		if numIters is not None:
			command += [ '--num-iterations', str(numIters) ]
		self.Shell( command )
