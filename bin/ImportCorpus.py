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

class ImportMallet( object ):
	
	def __init__( self, apps_root, app_name, logging_level ):
		self.app_name = app_name
		self.app_path = '{}/{}'.format( apps_root, app_name )
		self.app_data_corpus_path = '{}/{}/data/corpus'.format( apps_root, app_name )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.logger = logging.getLogger( 'ImportMallet' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def execute( self, filenameDocMetadata ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Importing corpus information as a model for app "%s"', self.app_name              )
		self.logger.info( '         app = %s', self.app_path                                                 )
		self.logger.info( '    doc-meta = %s', filenameDocMetadata                                           )
		self.logger.info( '--------------------------------------------------------------------------------' )
		
		if not os.path.exists( self.app_path ):
			self.logger.info( 'Creating output folder: %s', self.app_path )
			os.makedirs( self.app_path )
		if not os.path.exists( self.app_data_corpus_path ):
			self.logger.info( 'Creating app data folder: %s', self.app_data_corpus_path )
			os.makedirs( self.app_data_corpus_path )
		
		self.logger.info( 'Reading document metadata: %s', filenameDocMetadata )
		self.ExtractDocMetadata( filenameDocMetadata )
		
		self.logger.info( 'Writing data to disk: %s', self.app_data_corpus_path )
		self.SaveToDisk()
		
		self.logger.info( '--------------------------------------------------------------------------------' )
		
	def ExtractDocMetadata( self, filename ):
		with open( filename, 'r' ) as f:
			header = None
			meta = {}
			for index, line in enumerate( f ):
				values = line[:-1].decode( 'utf-8' ).split( '\t' )
				if header is None:
					header = values
				else:
					record = {}
					for n, value in enumerate( values ):
						if n < len(header):
							key = header[n]
						else:
							key = 'Field{:d}'.format( n+1 )
						record[ key ] = value
					key = record['DocID']
					meta[ key ] = record
		self.meta = meta
	
	def SaveToDisk( self ):
		if self.meta is not None:
			filename = '{}/doc-meta.json'.format( self.app_data_corpus_path )
			with open( filename, 'w' ) as f:
				json.dump( self.meta, f, encoding = 'utf-8', indent = 2, sort_keys = True )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str,                      help = 'Web2py application identifier'                   )
	parser.add_argument( 'meta_file'    , type = str,                      help = 'Document metadata as tab-delimited or JSON file' )
	parser.add_argument( '--apps_root'  , type = str, default = APPS_ROOT, help = 'Web2py application path.'                        )
	parser.add_argument( '--logging'    , type = int, default = 20       , help = 'Override default logging level.'                 )
	args = parser.parse_args()
	
	ImportMallet(
		apps_root = args.apps_root,
		app_name = args.app_name,
		logging_level = args.logging
	).execute(
		args.meta_file
	)

if __name__ == '__main__':
	main()
