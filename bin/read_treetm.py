#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")

import argparse
import logging
import os
from models.LDA_DB import LDA_DB
from modules.apps.CreateApp import CreateApp
from modules.readers.TreeTMReader import TreeTMReader

def ImportMalletLDA( app_name, model_path, corpus_path, database_path, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	app_path = 'apps/{}'.format( app_name )
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Import a ITM topic model as a web2py application...' )
	logger.info( '     app_path = %s', app_path )
	logger.info( '   model_path = %s', model_path )
	logger.info( '  corpus_path = %s', corpus_path )
	logger.info( 'database_path = %s', database_path )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists( app_path ):
		with CreateApp( app_name ) as app:
			with LDA_DB( app.GetDatabasePath() ) as lda_db:
				reader = TreeTMReader( model_path, lda_db )
				reader.Execute()
#			with TreeTMReader( database_path ) as reader:
#				reader.Execute()
	else:
		logger.info( '    Already available: %s', app_path )

def main():
	parser = argparse.ArgumentParser( description = 'Import a ITM topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str                     , help = 'Web2py application identifier' )
	parser.add_argument( 'model_path'   , type = str                     , help = 'Output of a ITM topic model' )
	parser.add_argument( 'corpus_path'  , type = str                     , help = 'Text corpus as a tab-delimited file' )
	parser.add_argument( 'database_path', type = str                     , help = 'Text corpus and metadata as a SQLite3 database' )
	parser.add_argument( '--quiet'      , const = True , default = False , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	ImportMalletLDA( args.app_name, args.model_path, args.corpus_path, args.database_path, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
