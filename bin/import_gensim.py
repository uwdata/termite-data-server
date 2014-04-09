#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
from importers.CreateApp import CreateApp
from importers.Corpus import Corpus
from importers.GensimLDA import GensimLDA

def ImportGensimLDA( app_name, model_path, corpus_path, meta_path, is_quiet, force_overwrite ):
	logger = logging.getLogger( 'termite' )
	logger.addHandler( logging.StreamHandler() )
	logger.setLevel( logging.INFO if is_quiet else logging.DEBUG )
	
	app_path = 'apps/{}'.format( app_name )
	logger.info( '--------------------------------------------------------------------------------' )
	logger.info( 'Import a Gensim LDA topic model as a web2py application...' )
	logger.info( '     app_path = %s', app_path )
	logger.info( '   model_path = %s', model_path )
	logger.info( '  corpus_path = %s', corpus_path )
	logger.info( '    meta_path = %s', meta_path )
	logger.info( '--------------------------------------------------------------------------------' )
	
	if force_overwrite or not os.path.exists( app_path ):
		with CreateApp( app_name ) as createApp:
			importGensimLDA = GensimLDA( createApp.GetPath(), model_path )
			if force_overwrite or not importGensimLDA.Exists():
				importGensimLDA.Execute()
			importCorpus = Corpus( createApp.GetPath(), corpus_path, meta_path )
			if force_overwrite or not importCorpus.Exists():
				importCorpus.Execute()
	else:
		logger.info( '    Already available: %s', app_path )
	
	logger.info( '--------------------------------------------------------------------------------' )

def main():
	parser = argparse.ArgumentParser( description = 'Import a Gensim topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str                     , help = 'Web2py application identifier' )
	parser.add_argument( 'model_path'   , type = str                     , help = 'Path of a Gensim LDA topic model' )
	parser.add_argument( 'corpus_path'  , type = str                     , help = 'Path of input text corpus' )
	parser.add_argument( 'meta_path'    , type = str   , default = None  , help = 'Path of optional corpus metadata', nargs = '?' )
	parser.add_argument( '--quiet'      , const = True , default = False , help = 'Show fewer debugging messages', action = 'store_const' )
	parser.add_argument( '--overwrite'  , const = True , default = False , help = 'Overwrite any existing model', action = 'store_const' )
	args = parser.parse_args()
	ImportGensimLDA( args.app_name, args.model_path, args.corpus_path, args.meta_path, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
