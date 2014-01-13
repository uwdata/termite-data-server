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
		self.app_data_treetm_path = '{}/{}/data/treetm'.format( apps_root, app_name )
		self.app_controller_path = '{}/{}/controllers'.format( apps_root, app_name )
		self.app_views_path = '{}/{}/views'.format( apps_root, app_name )
		self.app_static_path = '{}/{}/static'.format( apps_root, app_name )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.latest_run = self.GetLatestRun()
		self.logger = logging.getLogger( 'ImportTreeTM' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def Execute( self, filenameTopicWordWeights, filenameDocTopicMixtures ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Importing a tree topic model as a web2py application...'                          )
		self.logger.info( '       model = %s', self.model_path                                               )
		self.logger.info( '         app = %s', self.app_path                                                 )
		self.logger.info( '  latest-run = %d', self.latest_run                                               )
		self.logger.info( '--------------------------------------------------------------------------------' )
		
		if not os.path.exists( self.app_path ):
			self.logger.info( 'Creating output folder: %s', self.app_path )
			os.makedirs( self.app_path )
		if not os.path.exists( self.app_data_lda_path ):
			self.logger.info( 'Creating app data folder: %s', self.app_data_lda_path )
			os.makedirs( self.app_data_lda_path )
		if not os.path.exists( self.app_data_treetm_path ):
			self.logger.info( 'Creating app data folder: %s', self.app_data_treetm_path )
			os.makedirs( self.app_data_treetm_path )
		
		self.run_path = self.GetRunPath( self.latest_run )
		self.docs = None
		self.terms = None
		self.topics = None
		self.docPaths = None
		self.termFreqs = None
		self.topicFreqs = None
		self.docsAndTopics = None
		self.topicsAndTerms = None
		
		self.terms = self.ReadVocabFile()
		
		self.logger.info( 'Reading model.topics file: %s/%s', self.model_path, 'model.topics' )
		self.ReadModelTopicsFile()
		
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

	def GetRunPath( self, iter ):
		return '{}/{:06d}'.format( self.model_path, iter )

	def GetLatestRun( self ):
		latest_run = -1
		for filename in os.listdir( self.model_path ):
			path = '{}/{}'.format( self.model_path, filename )
			if os.path.isdir( path ):
				n = int( filename )
				latest_run = max( latest_run, n )
		return latest_run

	def ReadVocabFile( self ):
		filename = '{}/corpus.voc'.format( self.model_path )
		with open( filename ) as f:
			vocab = [ line.split( '\t' )[1] for line in f.read().splitlines() ]
		vocab.sort()
		return vocab

	def ReadModelTopicsFile( self ):
		lookup = { n : term for n, term in enumerate( self.terms ) }
		filename = '{}/model.topics'.format( self.run_path )
		topics = set()
		topicsAndTerms = {}
		try:
			with open( filename ) as f:
				topicLabels = []
				topicTermProbs = []
				topicIndex = -1
				topicStr = None
				mode = None
				for line in f.read().decode( 'utf-8' ).splitlines():
					if len(line) == 0:
						topicIndex += 1
						topics.add( topicIndex )
						topicsAndTerms[ topicIndex ] = {}
						continue
					if line == '--------------':
						mode = 'topic'
						continue
					if line == '------------------------':
						mode = 'term'
						continue
					if mode == 'topic':
						topicLabels.append( line )
						continue
					if mode == 'term':
						freq, term = line.split( '\t' )
						freq = float( freq )
						topicsAndTerms[ topicIndex ][ term ] = freq
		except IOError:
			pass
		self.topics = topics
		self.topicsAndTerms = topicsAndTerms

	def Package( self ):
		self.docs = []
		self.terms = sorted( self.terms )
		self.topics = sorted( self.topics )
		self.docIndex = []
		self.termIndex = [ None ] * len( self.terms )
		self.topicIndex = [ None ] * len( self.topics )
		self.termTopicMatrix = [ None ] * len( self.terms )
		self.docTopicMatrix = []
		
		for n, term in enumerate( self.terms ):
			self.termIndex[n] = {
				'index' : n,
				'text' : term
			}
		for n, topic in enumerate( self.topics ):
			self.topicIndex[n] = {
				'index' : n
			}
		for n, term in enumerate( self.terms ):
			row = [ 0.0 ] * len( self.topics )
			for topic in self.topics:
				if topic in self.topicsAndTerms and term in self.topicsAndTerms[ topic ]:
					row[ topic ] = self.topicsAndTerms[ topic ][ term ]
			self.termTopicMatrix[ n ] = row
	
	def SaveToDisk( self ):
		filename = '{}/doc-index.json'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		filename = '{}/term-index.json'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		filename = '{}/topic-index.json'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		filename = '{}/term-topic-matrix.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			for row in self.termTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )
		
		filename = '{}/doc-topic-matrix.txt'.format( self.app_data_lda_path )
		with open( filename, 'w' ) as f:
			for row in self.docTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )

def main():
	parser = argparse.ArgumentParser( description = 'Import a tree topic model as a web2py application.' )
	parser.add_argument( 'model_path'   , type = str,                               help = 'Tree topic model path.'                  )
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
	).Execute(
		args.topic_words,
		args.doc_topics
	)

if __name__ == '__main__':
	main()
