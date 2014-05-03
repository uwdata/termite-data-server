#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")

import argparse
import logging
import os
import shutil

from apps.CreateApp import CreateApp
from apps.SplitSentences import SplitSentences
from db.Corpus_DB import Corpus_DB
from db.BOW_DB import BOW_DB
from db.BOW_ComputeStats import BOW_ComputeStats
from db.LDA_DB import LDA_DB
from db.LDA_ComputeStats import LDA_ComputeStats
from db.ITM_DB import ITM_DB
from db.ITM_ComputeStats import ITM_ComputeStats
from readers.TreeTMReader import TreeTMReader

def ImportMalletLDA( app_name, model_path, corpus_path, database_path, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	app_path = 'apps/{}'.format( app_name )
	corpus_filename = '{}/corpus.txt'.format( corpus_path )
	database_filename = '{}/corpus.db'.format( database_path )
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Import an ITM topic model as a web2py application...' )
	logger.info( '           app_name = %s', app_name )
	logger.info( '           app_path = %s', app_path )
	logger.info( '         model_path = %s', model_path )
	logger.info( '    corpus_filename = %s', corpus_filename )
	logger.info( '  database_filename = %s', database_filename )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists( app_path ):
		with CreateApp(app_name) as app:
			# Import corpus (models/corpus.db, data/corpus.txt, data/sentences.txt)
			app_database_filename = '{}/corpus.db'.format( app.GetDatabasePath() )
			app_corpus_filename = '{}/corpus.txt'.format( app.GetDataPath() )
			app_sentences_filename = '{}/sentences.txt'.format( app.GetDataPath() )
			logger.info( 'Copying [%s] --> [%s]', database_filename, app_database_filename )
			shutil.copy( database_filename, app_database_filename )
			logger.info( 'Copying [%s] --> [%s]', corpus_filename, app_corpus_filename )
			shutil.copy( corpus_filename, app_corpus_filename )
			logger.info( 'Extracting [%s] --> [%s]', corpus_filename, app_sentences_filename )
			SplitSentences( corpus_filename, app_sentences_filename )
			
			# Import model (data/*)
			app_model_path = '{}/treetm'.format( app.GetDataPath() )
			logger.info( 'Copying [%s] --> [%s]', model_path, app_model_path )
			shutil.copytree( model_path, app_model_path )

			db_path = app.GetDatabasePath()
			with Corpus_DB(db_path) as corpus_db:
				
				# Create a bow-of-words language model
				with BOW_DB(db_path, isInit=True) as bow_db:
					bow_computer = BOW_ComputeStats(bow_db, corpus_db, app_corpus_filename, app_sentences_filename)
					bow_computer.Execute()

				# Compute derived-statistics about an LDA-like topic model
				with LDA_DB(db_path, isInit=True) as lda_db:
					treetm_reader = TreeTMReader(lda_db, app_model_path)
					treetm_reader.Execute()
					lda_computer = LDA_ComputeStats(lda_db, corpus_db)
					lda_computer.Execute()
				
				# Compute derived-statistics about an interactive topic model
				with ITM_DB(db_path, isInit=True) as itm_db:
					itm_computer = ITM_ComputeStats(itm_db, corpus_db)
					itm_computer.Execute()
	else:
		logger.info( '    Already available: %s', app_path )

def main():
	parser = argparse.ArgumentParser( description = 'Import a ITM topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str , help = 'Web2py application identifier' )
	parser.add_argument( 'model_path'   , type = str , help = 'A folder containing ITM topic model output' )
	parser.add_argument( 'corpus_path'  , type = str , help = 'A folder containing a text corpus as a tab-delimited file named "corpus.txt"' )
	parser.add_argument( 'database_path', type = str , help = 'A folder containing a text corpus and its metadata as a SQLite3 database named "corpus.db"' )
	parser.add_argument( '--quiet'      , const = True , default = False , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	ImportMalletLDA( args.app_name, args.model_path, args.corpus_path, args.database_path, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
