#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import os
import sqlite3
import sys

sys.path.append("web2py")
from models.Corpus_DB import Corpus_DB

def ImportFolder(corpus_folder):
	filenames = glob.glob(corpus_folder)
	for filename in sorted(filenames):
		with open(filename, 'r') as f:
			doc_content = f.read().decode('utf-8', 'ignore')
			yield filename, doc_content

def ImportFile(corpus_filename):
	with open(corpus_filename, 'r') as f:
		for index, line in enumerate(f):
			values = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
			if len(values) == 1:
				doc_id = 'doc{}'.format(index+1)
				doc_content = values[0]
			else:
				doc_id = values[0]
				doc_content = values[1]
			yield doc_id, doc_content

def ReadFromStdin():
	for index, line in enumerate(sys.stdin):
		values = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
		if len(values) == 1:
			doc_id = 'doc{}'.format(index+1)
			doc_content = values[0]
		else:
			doc_id = values[0]
			doc_content = values[1]
		yield doc_id, doc_content

def UpdateFieldsTable(fields, conn, cursor):
	records = [[index, field] for index, field in enumerate(fields)]
	with conn:
		conn.executemany('insert or ignore into fields(field_index, field_name) values (?, ?)', records)
	cursor.execute('select field_index, field_name from fields')
	field_indexes = {}
	for record in cursor:
		field_index, field_name = record
		field_indexes[field_name] = field_index
	return field_indexes

def UpdateDocsTable(doc_index, doc_id, conn):
	record = [doc_index, doc_id]
	with conn:
		conn.execute('insert or ignore into docs(doc_index, doc_id) values (?, ?)', record)

def UpdateCorpusTable(doc_index, fields, values, field_indexes, conn):
	records = [ [doc_index, field_indexes[field], values[index]] for index, field in enumerate(fields) ]
	with conn:
		conn.executemany('insert or ignore into corpus(doc_index, field_index, value) values (?, ?, ?)', records)

def CreateDatabase(corpus_filename_or_folder, database_path):
	if corpus_filename_or_folder is not None:
		if os.path.isfile(corpus_filename_or_folder):
			corpus_iterator = ImportFile(corpus_filename_or_folder)
		else:
			corpus_iterator = ImportFolder(corpus_filename_or_folder)
	else:
		corpus_iterator = ReadFromStdin()
		
	database_filename = '{}/{}'.format(database_path, Corpus_DB.FILENAME)
	with Corpus_DB(database_path, isInit=True) as _:
		print 'Importing into database at {}'.format(database_filename)
	
	conn = sqlite3.connect(database_filename)
	cursor = conn.cursor()
	fields = ['doc_id', 'doc_content']
	field_indexes = UpdateFieldsTable(fields, conn, cursor)
	for doc_index, (doc_id, doc_content) in enumerate(corpus_iterator):
		UpdateDocsTable(doc_index, doc_id, conn)
		UpdateCorpusTable(doc_index, fields, [doc_id, doc_content], field_indexes, conn)
	cursor.close()
	conn.close()
	
def main():
	parser = argparse.ArgumentParser( description = 'Import a TSV file or a folder into a SQLite3 Database.' )
	parser.add_argument( 'database', type = str, help = 'Output database folder, containing a file "corpus.db"' )
	parser.add_argument( 'corpus'  , type = str, help = 'Input corpus filename or folder', nargs = '?', default = None )
	args = parser.parse_args()
	CreateDatabase(args.corpus, args.database)

if __name__ == '__main__':
	main()
