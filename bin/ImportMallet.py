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

class ImportMallet( object ):
	
	def __init__( self, model_path, apps_root, app_name, logging_level ):
		self.model_path = model_path
		self.app_path = '{}/{}'.format( apps_root, app_name )
		self.app_data_lda_path = '{}/{}/data/lda'.format( apps_root, app_name )
		self.app_controller_path = '{}/{}/controllers'.format( apps_root, app_name )
		self.app_views_path = '{}/{}/views'.format( apps_root, app_name )
		self.app_static_path = '{}/{}/static'.format( apps_root, app_name )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.logger = logging.getLogger( 'ImportMallet' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def execute( self, filenameTopicWordWeights, filenameDocTopicMixtures ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Importing a MALLET topic model as a web2py application...'                        )
		self.logger.info( '       model = %s', self.model_path                                               )
		self.logger.info( '         app = %s', self.app_path                                                 )
		self.logger.info( ' topic-words = %s', filenameTopicWordWeights                                      )
		self.logger.info( '  doc-topics = %s', filenameDocTopicMixtures                                      )
		self.logger.info( '--------------------------------------------------------------------------------' )
		
		if not os.path.exists( self.app_path ):
			self.logger.info( 'Creating output folder: %s', self.app_path )
			os.makedirs( self.app_path )
		if not os.path.exists( self.app_data_lda_path ):
			self.logger.info( 'Creating app data folder: %s', self.app_data_lda_path )
			os.makedirs( self.app_data_lda_path )
		
		self.docs = None
		self.terms = None
		self.topics = None
		self.docPaths = None
		self.termFreqs = None
		self.topicFreqs = None
		self.docsAndTopics = None
		self.topicsAndTerms = None
		
		self.logger.info( 'Reading topic-term matrix: %s/%s', self.model_path, filenameTopicWordWeights )
		self.ExtractTopicWordWeights( filenameTopicWordWeights )
		
		self.logger.info( 'Reading doc-topic matrix: %s/%s', self.model_path, filenameDocTopicMixtures )
		self.ExtractDocTopicMixtures( filenameDocTopicMixtures )
		
		self.logger.info( 'Preparing output data...' )
		self.Package()
		
		self.logger.info( 'Writing data to disk: %s', self.app_data_lda_path )
		self.SaveToDisk()
		
		if not os.path.exists( self.app_controller_path ):
			self.logger.info( 'Setting up app controllers: %s', self.app_controller_path )
			os.system( 'ln -s ../../server_src/controllers {}'.format( self.app_controller_path ) )
		
		if not os.path.exists( self.app_views_path ):
			self.logger.info( 'Setting up app views: %s', self.app_views_path )
			os.system( 'ln -s ../../server_src/views {}'.format( self.app_views_path ) )
		
		if not os.path.exists( self.app_static_path ):
			self.logger.info( 'Setting up app static folder: %s', self.app_static_path )
			os.system( 'ln -s ../../server_src/static {}'.format( self.app_static_path ) )
		
		if not os.path.exists( self.web2py_app_path ):
			self.logger.info( 'Adding app to web2py server: %s', self.web2py_app_path )
			os.system( 'ln -s ../../../{} {}'.format( self.app_path, self.web2py_app_path ) )
		
		self.logger.info( '--------------------------------------------------------------------------------' )
	
	def ExtractTopicWordWeights( self, filename ):
		terms = set()
		topics = set()
		termFreqs = {}
		topicFreqs = {}
		topicsAndTerms = {}
		
		filename = '{}/{}'.format( self.model_path, filename )
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				topic, term, value = line.split( '\t' )
				topic = int( topic, 10 )
				value = float( value )
				if topic not in topics:
					topics.add( topic )
					topicFreqs[ topic ] = 0.0
					topicsAndTerms[ topic ] = {}
				if term not in terms:
					terms.add( term )
					termFreqs[ term ] = 0.0
				
				topicsAndTerms[ topic ][ term ] = value
				topicFreqs[ topic ] += value
				termFreqs[ term ] += value
		
		self.terms = terms
		self.topics = topics
		self.termFreqs = termFreqs
		self.topicFreqs = topicFreqs
		self.topicsAndTerms = topicsAndTerms
	
	def ExtractDocTopicMixtures( self, filename ):
		docs = set()
		topics = set()
		docPaths = {}
		topicFreqs = {}
		docsAndTopics = {}
		
		filename = '{}/{}'.format( self.model_path, filename )
		header = None
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				if header is None:
					header = line
				else:
					fields = line.split( '\t' )
					doc = int(fields[0])
					docPath = fields[1]
					topicKeys = [ int(field) for n, field in enumerate(fields[2:]) if n == 0 ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n == 1 ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if doc not in docs:
							docs.add( doc )
							docPaths[ doc ] = docPath
							docsAndTopics[ doc ] = {}
						if topic not in topics:
							topics.add( topic )
							topicFreqs[ topic ] = 0.0
						docsAndTopics[ doc ][ topic ] = value
						topicFreqs[ topic ] += value
		
		self.docs = docs
		self.docPaths = docPaths
		self.docsAndTopics = docsAndTopics
		assert( len(self.topics) == len(topics) )
		assert( len(self.topicFreqs) == len(topicFreqs) )
	
	def Package( self ):
		self.docs = sorted( self.docs )
		self.terms = sorted( self.terms )
		self.topics = sorted( self.topics )
		self.docIndex = [ None ] * len( self.docs )
		self.termIndex = [ None ] * len( self.terms )
		self.topicIndex = [ None ] * len( self.topics )
		self.termTopicMatrix = [ None ] * len( self.terms )
		self.docTopicMatrix = [ None ] * len( self.docs )
		
		for n, doc in enumerate( self.docs ):
			self.docIndex[n] = {
				'index' : n,
				'path' : self.docPaths[ doc ]
			}
		for n, term in enumerate( self.terms ):
			self.termIndex[n] = {
				'index' : n,
				'text' : term,
				'freq' : self.termFreqs[ term ]
			}
		for n, topic in enumerate( self.topics ):
			self.topicIndex[n] = {
				'index' : n,
				'freq' : self.topicFreqs[ topic ]
			}
		for n, term in enumerate( self.terms ):
			row = [ 0.0 ] * len( self.topics )
			for topic in self.topics:
				if topic in self.topicsAndTerms and term in self.topicsAndTerms[ topic ]:
					row[ topic ] = self.topicsAndTerms[ topic ][ term ]
			self.termTopicMatrix[ n ] = row
		for doc in self.docs:
			row = [ 0.0 ] * len( self.topics )
			for topic, value in self.docsAndTopics[ doc ].iteritems():
				row[ topic ] = value
			self.docTopicMatrix[ doc ] = row
	
	def SaveToDisk( self ):
		filename = '{}/doc-index.json'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-index.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			f.write( u'{}\t{}\n'.format( 'DocIndex', 'DocPath' ) )
			for d in self.docIndex:
				f.write( u'{}\t{}\n'.format( d['index'], d['path'] ) )
		
		filename = '{}/term-index.json'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			f.write( u'{}\n'.format( 'TermIndex', 'TermText' ) )
			for d in self.termIndex:
				f.write( u'{}\n'.format( d['index'], d['text'] ).encode( 'utf-8' ) )
		
		filename = '{}/topic-index.json'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			f.write( u'{}\t{}\n'.format( 'TopicIndex', 'TopicFreq' ) )
			for d in self.topicIndex:
				f.write( u'{}\t{}\n'.format( d['index'], d['freq'] ).encode( 'utf-8' ) )
		
		filename = '{}/term-topic-matrix.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			for row in self.termTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )
		
		filename = '{}/doc-topic-matrix.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			for row in self.docTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'model_path'   , type = str,                               help = 'MALLET topic model path.'                )
	parser.add_argument( 'app_name'     , type = str,                               help = 'Web2py application identifier'           )
	parser.add_argument( '--apps_root'  , type = str, default = APPS_ROOT         , help = 'Web2py application path.'                )
	parser.add_argument( '--topic_words', type = str, default = TOPIC_WORD_WEIGHTS, help = 'File containing topic vs. word weights.' )
	parser.add_argument( '--doc_topics' , type = str, default = DOC_TOPIC_MIXTURES, help = 'File containing doc vs. topic mixtures.' )
	parser.add_argument( '--logging'    , type = int, default = 20                , help = 'Override default logging level.'         )
	args = parser.parse_args()
	
	ImportMallet(
		model_path = args.model_path,
		apps_root = args.apps_root,
		app_name = args.app_name,
		logging_level = args.logging
	).execute(
		args.topic_words,
		args.doc_topics
	)

if __name__ == '__main__':
	main()
