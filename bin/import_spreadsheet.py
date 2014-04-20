#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sqlite3
import sys

from import_corpus import InitCorpusTable, InitFieldsTable, InitDocsTable
from import_corpus import UpdateCorpusTable, UpdateFieldsTable, UpdateDocsTable

DOC_ID = 'doc_id'
DOC_IDS = frozenset([DOC_ID, 'docid'])

DOC_CONTENT = 'doc_content'
DOC_CONTENTS = frozenset([DOC_CONTENT, 'doccontent', 'docbody', 'doc_body'])

def ImportSpreadsheet(corpus_filename):
	with open(corpus_filename, 'r') as f:
		for index, line in enumerate(f):
			values = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
			yield values

def ReadFromStdin():
	for index, line in enumerate(sys.stdin):
		values = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
		yield values

def CreateDatabase(corpus_filename, database_filename):
	if corpus_filename is not None:
		spreadsheet_iterator = ImportSpreadsheet(corpus_filename)
	else:
		spreadsheet_iterator = ReadFromStdin()

	conn = sqlite3.connect(database_filename)
	InitCorpusTable(conn)
	InitFieldsTable(conn)
	InitDocsTable(conn)
	cursor = conn.cursor()

	fields = None
	for values in spreadsheet_iterator:
		if fields is None:
			fields = []
			for field in values:
				if field.lower() in DOC_IDS:
					fields.append(DOC_ID)
				elif field.lower() in DOC_CONTENTS:
					fields.append(DOC_CONTENT)
				else:
					fields.append(field)
			field_indexes = UpdateFieldsTable(fields, conn, cursor)
			try:
				field_doc_id = fields.index('doc_id')
			except ValueError:
				sys.stderr.write('Missing field: doc_id\n')
				sys.exit(-1)
			try:
				fields.index('doc_content')
			except ValueError:
				sys.stderr.write('Missing field: doc_content\n')
				sys.exit(-1)
		else:
			doc_id = values[field_doc_id]
			doc_index = UpdateDocsTable(doc_id, conn, cursor)
			UpdateCorpusTable(doc_index, fields, values, field_indexes, conn, cursor)
			
	cursor.close()
	conn.close()

def main():
	parser = argparse.ArgumentParser( description = 'Import a spreadsheet into a SQLite3 Database.' )
	parser.add_argument( 'database', type = str, help = 'Output database filename' )
	parser.add_argument( 'corpus'  , type = str, help = 'Input spreadsheet filename', nargs = '?', default = None )
	args = parser.parse_args()
	CreateDatabase(args.corpus, args.database)

if __name__ == '__main__':
	main()
