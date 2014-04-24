#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import re
import sqlite3
import sys

sys.path.append("web2py")
from models.Corpus_DB import Corpus_DB

WHITESPACES = re.compile(r'[ \t\n\x0B\f\r]+')

def ExportCorpus(database_path, corpus_path):
	def ReadDatabase():
		database_filename = '{}/{}'.format(database_path, Corpus_DB.FILENAME)
		with Corpus_DB(database_path) as _:
			print 'Reading from {}'.format(database_filename)

		conn = sqlite3.connect(database_filename)
		cursor = conn.cursor()
		cursor.execute('select docs.doc_id, corpus.value from corpus inner join docs on corpus.doc_index = docs.doc_index inner join fields on corpus.field_index = fields.field_index where fields.field_name = "doc_content" order by docs.doc_id')
		for record in cursor:
			yield record[0], record[1]
		cursor.close()
		conn.close()

	def SantizeDocContent(doc_content):
		return WHITESPACES.sub(' ', doc_content)

	corpus_filename = '{}/corpus.txt'.format(corpus_path)
	if corpus_filename is None:
		for doc_id, doc_content in ReadDatabase():
			line = u'{}\t{}\n'.format(doc_id, SantizeDocContent(doc_content)).encode('utf-8')
			sys.stdout.write(line)
	else:
		print 'Writing to {}'.format(corpus_filename)
		with open(corpus_filename, 'w') as f:
			for doc_id, doc_content in ReadDatabase():
				line = u'{}\t{}\n'.format(doc_id, SantizeDocContent(doc_content)).encode('utf-8')
				f.write(line)

def main():
	parser = argparse.ArgumentParser( description = 'Export a corpus out of a SQLite3 Database.' )
	parser.add_argument( 'database', type = str, help = 'Input database folder, containing a file "corpus.db"' )
	parser.add_argument( 'corpus'  , type = str, help = 'Output corpus folder, containing a file "corpus.txt"', nargs = '?', default = None )
	args = parser.parse_args()
	ExportCorpus(args.database, args.corpus)

if __name__ == '__main__':
	main()
