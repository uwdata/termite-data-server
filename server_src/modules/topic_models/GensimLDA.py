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
	def __init__(self, corpusPath, modelPath, tokenRegex = None, numTopics = 20, numPasses = 1):
		self.corpusPath = corpusPath
		self.modelPath = modelPath
		self.tokenRegex = tokenRegex
		self.numTopics = numTopics
		self.numPasses = numPasses
	
	def Execute(self):
		gensimLDA = GensimLDA(self.corpusPath, self.modelPath)
		gensimLDA.Execute(self.tokenRegex, self.numTopics, self.numPasses)

class GensimTermiteCorpusReader(corpora.TextCorpus):
	WHITESPACES = re.compile(r'\W+')
	LINEBREAKS = re.compile(r'[\t\n\x0B\f\r]+')
	DEFAULT_TOKEN_REGEX = re.compile(r'^\w{3,}$')
	
	def __init__(self, corpusPath, tokenRegexStr):
		if tokenRegexStr is not None:
			self.tokenRegex = re.compile(tokenRegexStr)
		else:
			self.tokenRegex = GensimTermiteCorpusReader.DEFAULT_TOKEN_REGEX
		self.docIds = []
		corpora.TextCorpus.__init__(self, corpusPath)

	def preprocess(self, tokens):
		"""Lowercase, remove stopwords etc. from a list of unicode strings."""
		result = []
		for token in tokens:
			s = token.lower().encode('utf-8')
			if self.tokenRegex.match(s) is not None:
				result.append(s)
		return [token for token in result if token not in STOPWORDS]

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
						tokens = GensimTermiteCorpusReader.WHITESPACES.split(GensimTermiteCorpusReader.LINEBREAKS.sub(' ', f.read().decode('utf-8', 'ignore')).strip())
						yield self.preprocess(tokens)
						self.docIds.append(filename)
						total_docs += 1
		else:
			with utils.smart_open(self.input) as f:
				for line in f:
					docId, docContent = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
					tokens = GensimTermiteCorpusReader.WHITESPACES.split(docContent)
					yield self.preprocess(tokens)
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
