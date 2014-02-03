#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import math
import json

APPS_ROOT = 'apps'
WEB2PY_ROOT = 'tools/web2py'
TOPIC_WORD_WEIGHTS = 'topic-word-weights.txt'
DOC_TOPIC_MIXTURES = 'doc-topic-mixtures.txt'
SUBFOLDERS = [ 'models', 'views', 'controllers', 'static', 'modules' ]

class ImportMallet( object ):
	
	def __init__( self, app_name, app_model = 'lda', logging_level = 20 ):
		self.app_path = '{}/{}'.format( APPS_ROOT, app_name )
		self.app_data_path = '{}/{}/data/{}'.format( APPS_ROOT, app_name, app_model )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.logger = logging.getLogger( 'ImportMallet' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Import a MALLET topic model as a web2py application...'                           )
		self.logger.info( '         app = %s', app_name                                                      )
		self.logger.info( '       model = %s', app_model                                                     )
		self.logger.info( '        path = %s', self.app_path                                                 )
		self.logger.info( '      web2py = %s', self.web2py_app_path                                          )
		self.logger.info( '--------------------------------------------------------------------------------' )
		if not os.path.exists( self.app_path ):
			self.logger.info( 'Creating app folder: %s', self.app_path )
			os.makedirs( self.app_path )
		if not os.path.exists( self.app_data_path ):
			self.logger.info( 'Creating app subfolder: %s', self.app_data_path )
			os.makedirs( self.app_data_path )
		for subfolder in SUBFOLDERS:
			app_subpath = '{}/{}'.format( self.app_path, subfolder )
			if not os.path.exists( app_subpath ):
				self.logger.info( 'Linking app subfolder: %s', app_subpath )
				os.system( 'ln -s ../../server_src/{} {}/{}'.format( subfolder, self.app_path, subfolder ) )
		filename = '{}/__init__.py'.format( self.app_path )
		if not os.path.exists( filename ):
			self.logger.info( 'Setting up __init__.py' )
			os.system( 'touch {}'.format( filename ) )

	def AddToWeb2py( self ):
		if not os.path.exists( self.web2py_app_path ):
			self.logger.info( 'Adding app to web2py server: %s', self.web2py_app_path )
			os.system( 'ln -s ../../../{} {}'.format( self.app_path, self.web2py_app_path ) )
		self.logger.info( '--------------------------------------------------------------------------------' )

	def ExtractLDA( self, model_path, filenameTopicWordWeights, filenameDocTopicMixtures ):
		termSet, topicSet, termFreqs, topicFreqs, termsAndTopics = self.ExtractTopicWordWeights( model_path, filenameTopicWordWeights )
		docSet, _, docsAndTopics = self.ExtractDocTopicMixtures( model_path, filenameDocTopicMixtures )
		self.SaveToDisk( termSet, docSet, topicSet, termFreqs, topicFreqs, termsAndTopics, docsAndTopics )
	
	def ExtractTopicWordWeights( self, model_path, filename ):
		self.logger.info( 'Reading topic-term matrix: %s/%s', model_path, filename )
		termSet = set()
		topicSet = set()
		termFreqs = {}
		topicFreqs = {}
		termsAndTopics = {}
		filename = '{}/{}'.format( model_path, filename )
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				topic, term, value = line.split( '\t' )
				topic = topic.strip()
				value = float( value )
				if topic not in topicSet:
					topicSet.add( topic )
					topicFreqs[ topic ] = 0.0
				if term not in termSet:
					termSet.add( term )
					termFreqs[ term ] = 0.0
					termsAndTopics[ term ] = {}
				termsAndTopics[ term ][ topic ] = value
				topicFreqs[ topic ] += value
				termFreqs[ term ] += value
		return termSet, topicSet, termFreqs, topicFreqs, termsAndTopics
	
	def ExtractDocTopicMixtures( self, model_path, filename ):
		self.logger.info( 'Reading doc-topic matrix: %s/%s', model_path, filename )
		docSet = set()
		topicSet = set()
		docsAndTopics = {}
		filename = '{}/{}'.format( model_path, filename )
		header = None
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				if header is None:
					header = line
				else:
					fields = line.split( '\t' )
					docID = fields[1]
					topicKeys = [ field.strip() for n, field in enumerate(fields[2:]) if n == 0 ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n == 1 ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if docID not in docSet:
							docSet.add( docID )
							docsAndTopics[ docID ] = {}
						if topic not in topicSet:
							topicSet.add( topic )
						docsAndTopics[ docID ][ topic ] = value
		return docSet, topicSet, docsAndTopics
	
	def SaveToDisk( self, termSet, docSet, topicSet, termFreqs, topicFreqs, termsAndTopics, docsAndTopics ):
		self.logger.info( 'Writing data to disk: %s', self.app_data_path )
		docs = sorted( docSet )
		terms = sorted( termSet, key = lambda x : -termFreqs[x] )
		topics = sorted( topicSet, key = lambda x : int(x) )
		docIndex = [ None ] * len( docs )
		termIndex = [ None ] * len( terms )
		topicIndex = [ None ] * len( topics )
		for n, term in enumerate( terms ):
			termIndex[n] = {
				'text' : term,
				'freq' : termFreqs[ term ]
			}
		for n, doc in enumerate( docs ):
			docIndex[n] = {
				'docID' : doc
			}
		for n, topic in enumerate( topics ):
			topicIndex[n] = {
				'index' : topic,
				'freq' : topicFreqs[ topic ]
			}
		
		filename = '{}/doc-index.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-topic-matrix.txt'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( termsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-topic-matrix.txt'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( docsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		self.docs = docs
		self.terms = terms
		self.topics = topics
		self.termsAndTopics = termsAndTopics
		self.docsAndTopics = docsAndTopics

	def ComputeTopicCooccurrence( self ):
		self.logger.info( 'Computing topic co-occurrence...' )
		topics = self.topics
		matrix = [ [0.0]*len(topics) for i in range(len(topics)) ]
		for docID, topicMixture in self.docsAndTopics.iteritems():
			for i, firstTopic in enumerate(topics):
				for j, secondTopic in enumerate(topics):
					if firstTopic in topicMixture and secondTopic in topicMixture:
						matrix[i][j] += topicMixture[firstTopic] * topicMixture[secondTopic]
		filename = '{}/topic-cooccurrence.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( matrix, f, encoding = 'utf-8', indent = 2, sort_keys = True )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str,                               help = 'Web2py application identifier'              )
	parser.add_argument( 'model_path'   , type = str,                               help = 'MALLET topic model path.'                   )
	parser.add_argument( '--topic_words', type = str, default = TOPIC_WORD_WEIGHTS, help = 'File containing topic vs. word weights.'    )
	parser.add_argument( '--doc_topics' , type = str, default = DOC_TOPIC_MIXTURES, help = 'File containing doc vs. topic mixtures.'    )
	parser.add_argument( '--topic_cooccurrence', action = 'store_const', const = True, default = False, help = 'Compute topic co-occurrence statistics' )
	args = parser.parse_args()
	
	importer = ImportMallet( app_name = args.app_name )
	importer.ExtractLDA( args.model_path, args.topic_words, args.doc_topics )
	if args.topic_cooccurrence:
		importer.ComputeTopicCooccurrence()
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
