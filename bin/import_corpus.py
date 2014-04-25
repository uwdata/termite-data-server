#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")
from models import *

import argparse
import os

def ImportCorpus(corpus_filename_or_folder, database_path):
	database_filename = '{}/corpus.db'.format(database_path)
	print 'Importing file [{}] into database [{}]'.format(corpus_filename_or_folder, database_filename)
	
	with Corpus_DB(database_path, isInit=True) as corpusDB:
		if os.path.isfile(corpus_filename_or_folder):
			corpusDB.ImportFromFile(corpus_filename_or_folder)
		else:
			corpusDB.ImportFromFolder(corpus_filename_or_folder)

def main():
	parser = argparse.ArgumentParser( description = 'Import a file into a SQLite3 Database.' )
	parser.add_argument( 'database', type = str, help = 'Output database folder, containing a file "corpus.db"' )
	parser.add_argument( 'corpus'  , type = str, help = 'Input corpus filename or folder' )
	args = parser.parse_args()
	ImportCorpus(args.corpus, args.database)

if __name__ == '__main__':
	main()
