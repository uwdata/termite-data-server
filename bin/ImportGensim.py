#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import json
from gensim import corpora, models

APPS_ROOT = 'apps'
WEB2PY_ROOT = 'tools/web2py'
SUBFOLDERS = [ 'controllers', 'views', 'static', 'modules', 'models' ]

class ImportGensim( object ):
	
	def __init__( self, dictionary_filename, model_filename, app_name, logging_level ):
		self.dictionary_filename = dictionary_filename
		self.model_filename = model_filename
		self.app_path = '{}/{}'.format( APPS_ROOT, app_name )
		self.app_data_path = '{}/{}/data/lda'.format( APPS_ROOT, app_name )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.logger = logging.getLogger( 'ImportGensim' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def execute( self ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Importing a gensim topic model as a web2py application...'                        )
		self.logger.info( '         app = %s', self.app_path                                                 )
		self.logger.info( '       model = %s', self.model_filename                                           )
		self.logger.info( '  dictionary = %s', self.dictionary_filename                                      )
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
		
		self.logger.info( 'Reading from %s, %s', self.dictionary_filename, self.model_filename )
		self.ExtractGensimModel()
		
		self.logger.info( 'Writing data to disk: %s', self.app_data_path )
		self.SaveToDisk()
		
		if not os.path.exists( self.web2py_app_path ):
			self.logger.info( 'Adding app to web2py server: %s', self.web2py_app_path )
			os.system( 'ln -s ../../../{} {}'.format( self.app_path, self.web2py_app_path ) )
		
		self.logger.info( '--------------------------------------------------------------------------------' )
	
	def ExtractGensimModel( self ):
		termTexts = {}
		termLookup = {}
		dictionary = corpora.Dictionary.load( self.dictionary_filename )
		model = models.LdaModel.load( self.model_filename )
		for i in dictionary:
			termTexts[i] = dictionary[i]
			termLookup[dictionary[i]] = i
		topics = model.show_topics( topics = -1, topn = len(termTexts), formatted = False )

		self.docIndex = []
		self.termIndex = [ None ] * len( termTexts )
		self.topicIndex = [ None ] * len( topics )
		self.termTopicMatrix = [ None ] * len( termTexts )
		self.docTopicMatrix = []

		for termID, termText in termTexts.iteritems():
			self.termIndex[termID] = {
				'index' : termID,
				'text' : termText,
				'docFreq' : dictionary.dfs[termID]
			}
			self.termTopicMatrix[termID] = [ 0.0 ] * len( topics )
		for n, topic in enumerate( topics ):
			self.topicIndex[n] = {
				'index' : n
			}
			for freq, termText in topic:
				termID = termLookup[ termText ]
				self.termTopicMatrix[ termID ][ n ] = freq

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
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'dictionary' , type = str,               help = 'File containing a gensim dictionary'        )
	parser.add_argument( 'model'      , type = str,               help = 'File containing a gensim LDA model'         )
	parser.add_argument( 'app_name'   , type = str,               help = 'Web2py application identifier'              )
	parser.add_argument( '--logging'  , type = int, default = 20, help = 'Override default logging level.'            )
	args = parser.parse_args()
	
	ImportGensim(
		dictionary_filename = args.dictionary,
		model_filename = args.model,
		app_name = args.app_name,
		logging_level = args.logging
	).execute()

if __name__ == '__main__':
	main()
