#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

APPS_ROOT = 'apps'
WEB2PY_ROOT = 'web2py'
SUBFOLDERS = [ 'models', 'views', 'controllers', 'static', 'modules' ]

class ImportAbstraction( object ):
	
	def __init__( self, app_name, app_model, app_desc ):
		self.app_desc = app_desc
		self.app_name = app_name
		self.app_model = app_model
		self.app_path = '{}/{}'.format( APPS_ROOT, app_name )
		self.data_path = '{}/{}/data/{}'.format( APPS_ROOT, app_name, app_model )
		self.web2py_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.database_path = '{}/{}/databases'.format( APPS_ROOT, app_name )
	
	def AddAppFolder( self ):
		if os.path.exists( self.data_path ):
			return False
		
		print '--------------------------------------------------------------------------------'
		print 'Import "{}" as a web2py application...'.format( self.app_desc )
		print '          app = {}'.format( self.app_name )
		print '        model = {}'.format( self.app_model )
		print '     app_path = {}'.format( self.app_path )
		print '    data_path = {}'.format( self.data_path )
		print 'database_path = {}'.format( self.database_path )
		print '  web2py_path = {}'.format( self.web2py_path )
		print '--------------------------------------------------------------------------------'
		
		if not os.path.exists( self.app_path ):
			print 'Creating app folder: {}'.format( self.app_path )
			os.makedirs( self.app_path )
		
		if not os.path.exists( self.data_path ):
			print 'Creating data subfolder: {}'.format( self.data_path )
			os.makedirs( self.data_path )
		
		if not os.path.exists( self.database_path ):
			print 'Creating database subfolder: {}'.format( self.database_path )
			os.makedirs( self.database_path )
		
		for subfolder in SUBFOLDERS:
			app_subpath = '{}/{}'.format( self.app_path, subfolder )
			if not os.path.exists( app_subpath ):
				print 'Linking subfolder: {}'.format( app_subpath )
				os.system( 'ln -s ../../server_src/{} {}/{}'.format( subfolder, self.app_path, subfolder ) )
		
		filename = '{}/__init__.py'.format( self.app_path )
		if not os.path.exists( filename ):
			print 'Setting up __init__.py'
			os.system( 'touch {}'.format( filename ) )
		
		return True
	
	def ResolveMatrices( self ):
		index_filename = '{}/term-index.json'.format( self.data_path )
		original_filename = '{}/term-topic-matrix.txt'.format( self.data_path )
		resolved_filename = '{}/term-topic-matrix.json'.format( self.data_path )
		with open( index_filename, 'r' ) as f:
			index = json.load( f, encoding = 'utf-8' )
		with open( original_filename, 'r' ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		resolved = self.ResolveMatrix( matrix, [ d['text'] for d in index ] )
		with open( resolved_filename, 'w' ) as f:
			json.dump( resolved, f, encoding = 'utf-8', indent = 2, sort_keys = True )

		index_filename = '{}/doc-index.json'.format( self.data_path )
		original_filename = '{}/doc-topic-matrix.txt'.format( self.data_path )
		resolved_filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		with open( index_filename, 'r' ) as f:
			index = json.load( f, encoding = 'utf-8' )
		with open( original_filename, 'r' ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		resolved = self.ResolveMatrix( matrix, [ d['docID'] for d in index ] )
		with open( resolved_filename, 'w' ) as f:
			json.dump( resolved, f, encoding = 'utf-8', indent = 2, sort_keys = True )
	
	def ResolveMatrix( self, matrix, keys ):
		resolved = {}
		assert len( matrix ) == len( keys )
		for i, key in enumerate( keys ):
			resolved[ key ] = matrix[ i ]
		return resolved
			
	def TransposeMatrices( self ):
		original_filename = '{}/term-topic-matrix.json'.format( self.data_path )
		transposed_filename = '{}/topic-term-matrix.json'.format( self.data_path )
		with open( original_filename, 'r' ) as f:
			termsAndTopics = json.load( f, encoding = 'utf-8' )
		topicsAndTerms = self.TransposeMatrix( termsAndTopics )
		with open( transposed_filename, 'w' ) as f:
			json.dump( topicsAndTerms, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		original_filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		transposed_filename = '{}/topic-doc-matrix.json'.format( self.data_path )
		with open( original_filename, 'r' ) as f:
			docsAndTopics = json.load( f, encoding = 'utf-8' )
		topicsAndDocs = self.TransposeMatrix( docsAndTopics )
		with open( transposed_filename, 'w' ) as f:
			json.dump( topicsAndDocs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
	
	def TransposeMatrix( self, matrix ):
		transposed = []
		for key, values in matrix.iteritems():
			for index, value in enumerate( values ):
				while len( transposed ) <= index:
					transposed.append( {} )
				transposed[ index ][ key ] = value
		return transposed
		
	def AddToWeb2py( self ):
		if not os.path.exists( self.web2py_path ):
			print 'Adding app to web2py server: {}'.format( self.web2py_path )
			os.system( 'ln -s ../../{} {}'.format( self.app_path, self.web2py_path ) )
		print '--------------------------------------------------------------------------------'
