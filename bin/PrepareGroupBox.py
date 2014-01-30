#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import math
import re
import json
import glob
from ImportMallet import ImportMallet

APPS_ROOT = 'apps'
WEB2PY_ROOT = 'tools/web2py'
TOPIC_WORD_WEIGHTS = 'topic-word-weights.txt'
DOC_TOPIC_MIXTURES = 'doc-topic-mixtures.txt'
SUBFOLDERS = [ 'controllers', 'views', 'static', 'modules', 'models' ]

class PrepareGroupBox( object ):
	
	def __init__( self, app_name, logging_level ):
		self.app_name = app_name
		self.app_path = '{}/{}'.format( APPS_ROOT, app_name )
		self.app_data_path = '{}/{}/data/group_box'.format( APPS_ROOT, app_name )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.logger = logging.getLogger( 'PrepareGroupBox' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def execute( self, corpus_path, model_path ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Preparing term co-occurrence stats "%s"', self.app_name                           )
		self.logger.info( '         app = %s', self.app_path                                                 )
		self.logger.info( '      corpus = %s', corpus_path                                                   )
		self.logger.info( '       model = %s', model_path                                                    )
		self.logger.info( '--------------------------------------------------------------------------------' )
		
		if not os.path.exists( self.app_path ):
			self.logger.info( 'Creating app folder: %s', self.app_path )
			os.makedirs( self.app_path )
		if not os.path.exists( self.app_data_path ):
			self.logger.info( 'Creating app data folder: %s', self.app_data_path )
			os.makedirs( self.app_data_path )
		for subfolder in SUBFOLDERS:
			path = '{}/{}'.format( self.app_path, subfolder )
			if not os.path.exists( path ):
				self.logger.info( 'Setting up app %s: %s', subfolder, path )
				os.system( 'ln -s ../../server_src/{} {}/{}'.format( subfolder, self.app_path, subfolder ) )
		filename = '{}/__init__.py'.format( self.app_path )
		if not os.path.exists( filename ):
			self.logger.info( 'Setting up __init__.py' )
			os.system( 'touch {}'.format( filename ) )
		
		self.logger.info( 'Reading topic-term matrix: %s/%s', model_path, TOPIC_WORD_WEIGHTS )
		self.termSet, self.topicSet, self.termFreqs, self.topicFreqs, self.topicsAndTerms = self.ExtractTopicWordWeights( model_path, TOPIC_WORD_WEIGHTS )

		self.logger.info( 'Reading doc-topic matrix: %s/%s', model_path, DOC_TOPIC_MIXTURES )
		self.docSet, self.docIDs, self.docsAndTopics = self.ExtractDocTopicMixtures( model_path, DOC_TOPIC_MIXTURES )
		
		self.logger.info( 'Reading corpus...' )
		self.docsAndTokens = self.LoadCorpus( corpus_path )

		self.logger.info( 'Computing term co-occurrence...' )
		self.ComputeTermCooccurrence()
		
		self.logger.info( 'Computing topic co-occurrence...' )
		self.ComputeTopicCooccurrence()

		self.logger.info( 'Preparing output data...' )
		self.Package()
		
		self.logger.info( 'Writing data to disk: %s', self.app_data_path )
		self.SaveToDisk()
		
		if not os.path.exists( self.web2py_app_path ):
			self.logger.info( 'Adding app to web2py server: %s', self.web2py_app_path )
			os.system( 'ln -s ../../../{} {}'.format( self.app_path, self.web2py_app_path ) )

		self.logger.info( '--------------------------------------------------------------------------------' )
	
	def LoadCorpus( self, corpus_path ):
		docsAndTokens = {}
		pattern = re.compile( r'[a-zA-Z]+' )
		if os.path.exists( corpus_path ):
			if os.path.isdir( corpus_path ):
				filenames = glob.glob( '{}/*/*'.format( corpus_path ) )
				for filename in filenames:
					with open( filename, 'r' ) as f:
						docContent = f.read().decode( 'utf-8', 'ignore' )
						tokens = pattern.findall( docContent )
						docsAndTokens[ filename ] = [ token.lower() for token in tokens if len(token) >= 3 ]
			else:
				with open( corpus_path, 'r' ) as f:
					for line in f:
						line = line[:-1].decode( 'utf-8' )
						docID, docContent = line.split( '\t' )
						tokens = pattern.findall( docContent )
						docsAndTokens[ docID ] = [ token.lower() for token in tokens if len(token) >= 3 ]
		return docsAndTokens
						
	def ComputeTermCooccurrence( self ):
		terms = sorted( self.termSet )
		matrix = {}
		for docID, tokens in self.docsAndTokens.iteritems():
			for firstTerm in tokens:
				for secondTerm in tokens:
					if firstTerm not in matrix:
						matrix[firstTerm] = {}
					if secondTerm not in matrix[firstTerm]:
						matrix[firstTerm][secondTerm] = 0.0
					matrix[firstTerm][secondTerm] += 1.0
		filename = '{}/term-cooccurrence.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( matrix, f, encoding = 'utf-8' )

	def ComputeTopicCooccurrence( self ):
		topics = sorted( self.topicSet )

		matrix = [ [0.0]*len(topics) for i in range(len(topics)) ]
		for docID, topicMixture in self.docsAndTopics.iteritems():
			for i, firstTopic in enumerate(topics):
				for j, secondTopic in enumerate(topics):
					if firstTopic in topicMixture and secondTopic in topicMixture:
						matrix[i][j] += topicMixture[firstTopic] * topicMixture[secondTopic]
		filename = '{}/topic-cooccurrence.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( matrix, f, encoding = 'utf-8' )
		
	def ExtractTopicWordWeights( self, model_path, filename ):
		termSet = set()
		topicSet = set()
		termFreqs = {}
		topicFreqs = {}
		topicsAndTerms = {}

		filename = '{}/{}'.format( model_path, filename )
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				topic, term, value = line.split( '\t' )
				topic = int( topic, 10 )
				value = float( value )
				if topic not in topicSet:
					topicSet.add( topic )
					topicFreqs[ topic ] = 0.0
					topicsAndTerms[ topic ] = {}
				if term not in termSet:
					termSet.add( term )
					termFreqs[ term ] = 0.0

				topicsAndTerms[ topic ][ term ] = value
				topicFreqs[ topic ] += value
				termFreqs[ term ] += value

		return termSet, topicSet, termFreqs, topicFreqs, topicsAndTerms

	def ExtractDocTopicMixtures( self, model_path, filename ):
		docSet = set()
		topicSet = set()
		docIDs = {}
		topicFreqs = {}
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
					doc = int(fields[0])
					docID = fields[1]
					topicKeys = [ int(field) for n, field in enumerate(fields[2:]) if n == 0 ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n == 1 ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if doc not in docSet:
							docSet.add( doc )
							docIDs[ doc ] = docID
							docsAndTopics[ doc ] = {}
						if topic not in topicSet:
							topicSet.add( topic )
							topicFreqs[ topic ] = 0.0
						docsAndTopics[ doc ][ topic ] = value
						topicFreqs[ topic ] += value

		assert( len(self.topicSet) == len(topicSet) )
		assert( len(self.topicFreqs) == len(topicFreqs) )
		return docSet, docIDs, docsAndTopics

	def Package( self ):
		docs = sorted( self.docSet )
		terms = sorted( self.termSet )
		topics = sorted( self.topicSet )
		self.docIndex = [ None ] * len( docs )
		self.termIndex = [ None ] * len( terms )
		self.topicIndex = [ None ] * len( topics )
		self.termTopicMatrix = [ None ] * len( terms )
		self.docTopicMatrix = [ None ] * len( docs )

		for n, doc in enumerate( docs ):
			self.docIndex[n] = {
				'index' : n,
				'docID' : self.docIDs[ doc ]
			}
		for n, term in enumerate( terms ):
			self.termIndex[n] = {
				'index' : n,
				'text' : term,
				'freq' : self.termFreqs[ term ]
			}
		for n, topic in enumerate( topics ):
			self.topicIndex[n] = {
				'index' : n,
				'freq' : self.topicFreqs[ topic ]
			}
		for n, term in enumerate( terms ):
			row = [ 0.0 ] * len( topics )
			for topic in topics:
				if topic in self.topicsAndTerms and term in self.topicsAndTerms[ topic ]:
					row[ topic ] = self.topicsAndTerms[ topic ][ term ]
			self.termTopicMatrix[ n ] = row
		for doc in docs:
			row = [ 0.0 ] * len( topics )
			for topic, value in self.docsAndTopics[ doc ].iteritems():
				row[ topic ] = value
			self.docTopicMatrix[ doc ] = row

	def SaveToDisk( self ):
		filename = '{}/doc-index.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )

		filename = '{}/term-index.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )

		filename = '{}/topic-index.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )

		filename = '{}/term-topic-matrix.txt'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			for row in self.termTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )

		filename = '{}/doc-topic-matrix.txt'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			for row in self.docTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )
def main():
	parser = argparse.ArgumentParser( description = 'Prepare a MALLET topic model for group-in-a-box visualization.' )
	parser.add_argument( 'corpus_path'  , type = str,                               help = 'Text corpus path'                           )
	parser.add_argument( 'model_path'   , type = str,                               help = 'MALLET topic model path.'                   )
	parser.add_argument( 'app_name'     , type = str,                               help = 'Web2py application identifier'              )
	parser.add_argument( '--topic_words', type = str, default = TOPIC_WORD_WEIGHTS, help = 'File containing topic vs. word weights.'    )
	parser.add_argument( '--doc_topics' , type = str, default = DOC_TOPIC_MIXTURES, help = 'File containing doc vs. topic mixtures.'    )
	parser.add_argument( '--logging'    , type = int, default = 20                , help = 'Override default logging level.'            )
	args = parser.parse_args()
	
	PrepareGroupBox(
		app_name = args.app_name,
		logging_level = args.logging
	).execute(
		model_path = args.model_path,
		corpus_path = args.corpus_path
	)

if __name__ == '__main__':
	main()
