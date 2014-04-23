#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import shutil
import sys
from modules.apps.CreateApp import CreateApp
from modules.apps.ComputeCorpusStats import ComputeCorpusStats
from modules.apps.ComputeLDAStats import ComputeLDAStats
from modules.readers.MalletReader import MalletReader

sys.path.append("web2py")
from models.Corpus_DB import Corpus_DB
from models.CorpusStats_DB import CorpusStats_DB
from models.LDA_DB import LDA_DB
from models.LDAStats_DB import LDAStats_DB

def ImportMalletLDA( app_name, model_path, corpus_path, database_path, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	app_path = 'apps/{}'.format( app_name )
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Import a MALLET LDA topic model as a web2py application...' )
	logger.info( '     app_path = %s', app_path )
	logger.info( '   model_path = %s', model_path )
	logger.info( '  corpus_path = %s', corpus_path )
	logger.info( 'database_path = %s', database_path )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists( app_path ):
		with CreateApp(app_name) as app:
			app_model_path = '{}/mallet-lda'.format( app.GetDataPath() )
			app_corpus_path = '{}/corpus.txt'.format( app.GetDataPath() )
			app_database_path = '{}/corpus.db'.format( app.GetDatabasePath() )
			logger.info( 'Copying [%s] --> [%s]', model_path, app_model_path )
			shutil.copytree( model_path, app_model_path )
			logger.info( 'Copying [%s] --> [%s]', corpus_path, app_corpus_path )
			shutil.copy( corpus_path, app_corpus_path )
			logger.info( 'Copying [%s] --> [%s]', database_path, app_database_path )
			shutil.copy( database_path, app_database_path )
			
			db_path = app.GetDatabasePath()
			with LDA_DB(db_path) as lda_db:
				reader = MalletReader( app_model_path, lda_db )
				reader.Execute()
				with LDAStats_DB(db_path) as ldaStats_db:
					computer = ComputeLDAStats( lda_db, ldaStats_db )
					computer.Execute()
			with Corpus_DB(db_path) as corpus_db:
				with CorpusStats_DB(db_path) as corpusStats_db:
					computer = ComputeCorpusStats( corpus_db, corpusStats_db )
					computer.Execute()
	else:
		logger.info( '    Already available: %s', app_path )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str                     , help = 'Web2py application identifier' )
	parser.add_argument( 'model_path'   , type = str                     , help = 'Output of a MALLET LDA topic model' )
	parser.add_argument( 'corpus_path'  , type = str                     , help = 'Text corpus as a tab-delimited file' )
	parser.add_argument( 'database_path', type = str                     , help = 'Text corpus and metadata as a SQLite3 database' )
	parser.add_argument( '--quiet'      , const = True , default = False , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	ImportMalletLDA( args.app_name, args.model_path, args.corpus_path, args.database_path, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
