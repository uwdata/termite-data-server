#!/usr/bin/env python

import subprocess

class LDA(object):
	def __init__( self, malletPath = 'tools/mallet', modelPath = 'data', numTopics = 20, numIters = 1000 ):
		self.malletPath = malletPath
		self.modelPath = modelPath
		self.numTopics = numTopics
		self.numIters = numIters
		self.inputCorpus = '{}/corpus.mallet'.format( self.modelPath )
		self.outputModel = '{}/output.model'.format( self.modelPath )
		self.outputTopicKeys = '{}/output-topic-keys.txt'.format( self.modelPath )
		self.outputTopicWordWeights = '{}/topic-word-weights.txt'.format( self.modelPath )
		self.outputDocTopicMixtures = '{}/doc-topic-mixtures.txt'.format( self.modelPath )
		self.outputWordTopicCounts = '{}/word-topic-counts.txt'.format( self.modelPath )
		
	def Execute( self ):
		mallet_executable = '{}/bin/mallet'.format( self.malletPath )
		command = [
			mallet_executable, 'train-topics',
			'--input', self.inputCorpus,
			'--output-model', self.outputModel,
			'--output-topic-keys', self.outputTopicKeys,
			'--topic-word-weights-file', self.outputTopicWordWeights,
			'--output-doc-topics', self.outputDocTopicMixtures,
			'--word-topic-counts-file', self.outputWordTopicCounts,
			'--num-topics', str(self.numTopics),
			'--num-iterations', str(self.numIters)
		]
		process = subprocess.call( command )
