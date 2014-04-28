#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import logging
import os
import re
from gensim import corpora, models, utils
from gensim.parsing.preprocessing import STOPWORDS

class BuildLDA(object):
	"""
	corpusPath = A single tab-delimited file containing the corpus (one document per line, two columns containing docID and docContent, without headers)
	modelPath = Folder for storing all output files
	tokenRegex, numTopics, numPasses = Other parameters
	"""
	def __init__(self, corpusPath, modelPath, tokenRegex = r'\w{3,}', numTopics = 20, numPasses = 1):
		gensimLDA = GensimLDA(corpusPath, modelPath)
		gensimLDA.Execute(tokenRegex, numTopics, numPasses)

class GensimTermiteCorpusReader(corpora.TextCorpus):
	DEFAULT_TOKEN_REGEX = re.compile(r'\w{3,}')
	
	def __init__(self, corpusPath, tokenRegexStr):
		if tokenRegexStr is None:
			tokenRegexStr = GensimTermiteCorpusReader.DEFAULT_TOKEN_REGEX
		self.tokenRegexStr = tokenRegexStr
		self.tokenRegex = re.compile(self.tokenRegexStr)
		self.docIds = []
		corpora.TextCorpus.__init__(self, corpusPath)

	def get_texts(self):
		total_docs = 0
		if os.path.isdir( self.input ):
			# Read two levels of files
			filenames = glob.glob('{}/*'.format(self.input))
			for filename in filenames:
				if os.path.isdir(filename):
					filenames += glob.glob('{}/*'.format(filename))
			for filename in filenames:
				if not os.path.isdir( filename ):
					with utils.smart_open( filename ) as f:
						docId = filename
						docContent = u' '.join(f.read().decode('utf-8', 'ignore').splitlines())
						tokens = self.tokenRegex.findall(docContent)
						tokens = [token.lower().encode('utf-8') for token in tokens if token not in STOPWORDS]
						yield tokens
						self.docIds.append(docId)
						total_docs += 1
		else:
			with utils.smart_open(self.input) as f:
				for line in f:
					docId, docContent = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
					tokens = self.tokenRegex.findall(docContent)
					tokens = [token.lower().encode('utf-8') for token in tokens if token not in STOPWORDS]
					yield tokens
					self.docIds.append(docId)
					total_docs += 1
		self.length = total_docs

class GensimLDA( object ):
	DICTIONARY_FILENAME = 'dictionary.gensim'
	CORPUS_FILENAME = 'corpus.gensim'
	MODEL_FILENAME = 'lda.gensim'

	def __init__( self, corpusPath, modelPath ):
		self.logger = logging.getLogger('termite')
		self.corpusPath = corpusPath
		self.modelPath = modelPath
		self.dictionaryInGensim = '{}/{}'.format( self.modelPath, GensimLDA.DICTIONARY_FILENAME )
		self.corpusInGensim = '{}/{}'.format( self.modelPath, GensimLDA.CORPUS_FILENAME )
		self.modelInGensim = '{}/{}'.format( self.modelPath, GensimLDA.MODEL_FILENAME )

	def Execute( self, tokenRegex, numTopics, numPasses ):
		if not os.path.exists( self.modelPath ):
			os.makedirs( self.modelPath )

		# Generate gensim objects
		corpus = GensimTermiteCorpusReader( self.corpusPath, tokenRegex )
		corpus.dictionary.filter_extremes( no_above = 0.2 )  # remove words that are too frequent/too infrequent
		model = models.LdaModel( corpus, id2word = corpus.dictionary, num_topics = numTopics, passes = numPasses )

		self.logger.info( 'Saving dictionary to disk: %s', self.dictionaryInGensim )
		corpus.dictionary.save( self.dictionaryInGensim )
		
		self.logger.info( 'Saving corpus to disk: %s', self.corpusInGensim )
		corpus.save( self.corpusInGensim )

		self.logger.info( 'Saving model to disk: %s', self.modelInGensim )
		model.save( self.modelInGensim )
