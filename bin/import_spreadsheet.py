#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")

import argparse
from db.Corpus_DB import Corpus_DB

def ImportSpreadsheet(spreadsheet_filename, database_path, id_key, content_key, is_csv):
	database_filename = '{}/corpus.db'.format(database_path)
	print 'Importing spreadsheet [{}] into database [{}]'.format(spreadsheet_filename, database_filename)
	
	with Corpus_DB(database_path, isImport=True) as corpus_db:
		corpus_db.ImportFromSpreadsheet(spreadsheet_filename, is_csv = is_csv, id_key = id_key, content_key = content_key)

def main():
	parser = argparse.ArgumentParser( description = 'Import a tab-delimited spreadsheet into a SQLite3 Database.' )
	parser.add_argument( 'database' , type = str  , help = 'Output database folder, containing a file "corpus.db"' )
	parser.add_argument( 'corpus'   , type = str  , help = 'Input spreadsheet filename' )
	parser.add_argument( '--id'     , type = str  , default = None , help = 'Name of the column containing doc_id, which must be unique for all rows' )
	parser.add_argument( '--content', type = str  , default = None , help = 'Name of the column containing doc_content' )
	parser.add_argument( '--csv'    , const = True, default = False, help = 'Use a comma-separated spreadsheet', action = 'store_const' )
	args = parser.parse_args()
	ImportSpreadsheet(args.corpus, args.database, args.id, args.content, args.csv)

if __name__ == '__main__':
	main()
