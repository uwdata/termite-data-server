#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")

import csv
csv.field_size_limit(sys.maxsize)

import argparse
from db.Corpus_DB import Corpus_DB

def ExportSpreadsheet(database_path, spreadsheet_filename, id_key, content_key, is_csv):
	database_filename = '{}/corpus.db'.format(database_path)
	print 'Exporting database [{}] to spreadsheet [{}]'.format(database_filename, spreadsheet_filename)
	
	with Corpus_DB(database_path) as corpus_db:
		corpus_db.ExportToSpreadsheet(spreadsheet_filename, is_csv = is_csv, id_key = id_key, content_key = content_key)

def main():
	parser = argparse.ArgumentParser( description = 'Export a corpus out of a SQLite3 Database.' )
	parser.add_argument( 'database', type = str, help = 'Input database folder, containing a file "corpus.db"' )
	parser.add_argument( 'corpus'  , type = str, help = 'Output speadsheet filename' )
	parser.add_argument( '--id'     , type = str  , default = None , help = 'Name of the column containing doc_id, which must be unique for all rows' )
	parser.add_argument( '--content', type = str  , default = None , help = 'Name of the column containing doc_content' )
	parser.add_argument( '--csv'    , const = True, default = False, help = 'Use a comma-separated spreadsheet', action = 'store_const' )
	args = parser.parse_args()
	ExportSpreadsheet(args.database, args.corpus, args.id, args.content, args.csv)

if __name__ == '__main__':
	main()
