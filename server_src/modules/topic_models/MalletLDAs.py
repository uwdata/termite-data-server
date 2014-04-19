#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from MalletLDA import MalletLDA

class MalletLDAs(object):
	def __init__( self, corpusPath, modelPath = 'data', tokenRegex = '\p{Alpha}{3,}', numTopics = 20, numIters = 1000, numModels = 50, MALLET_PATH = 'tools/mallet' ):
		self.MALLET_PATH = MALLET_PATH
		self.logger = logging.getLogger('termite')
		
		self.corpusPath = corpusPath
		self.modelPath = modelPath
		self.tokenRegex = tokenRegex
		self.numTopics = numTopics
		self.numIters = numIters
		self.numModels = numModels

	def Execute( self ):
		self.logger.info( 'Building a batch of %d topic models', self.numModels )
		if not os.path.exists( self.modelPath ):
			os.makedirs( self.modelPath )
		for n in range(self.numModels):
			modelSubPath = '{}/{}'.format( self.modelPath, n )
			malletLDA = MalletLDA( self.corpusPath, modelSubPath, self.tokenRegex, self.numTopics, self.numIters, self.MALLET_PATH )
			malletLDA.Execute()
