#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")

import argparse
from db.Corpus_DB import Corpus_DB

def ExportCorpus(database_path, corpus_filename):
	database_filename = '{}/corpus.db'.format(database_path)
	print 'Exporting database [{}] to file [{}]'.format(database_filename, corpus_filename)
	
	with Corpus_DB(database_path) as corpusDB:
		corpusDB.ExportToFile(corpus_filename)

def main():
	parser = argparse.ArgumentParser( description = 'Export a corpus out of a SQLite3 Database.' )
	parser.add_argument( 'database', type = str, help = 'Input database folder, containing a file "corpus.db"' )
	parser.add_argument( 'corpus'  , type = str, help = 'Output corpus filename' )
	args = parser.parse_args()
	ExportCorpus(args.database, args.corpus)

if __name__ == '__main__':
	main()
