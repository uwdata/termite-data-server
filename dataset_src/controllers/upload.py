#!/usr/bin/env python

import os
from db.Corpus_DB import Corpus_DB

def index():
	return {}

def spreadsheet():
	def ImportSpreadsheet(dataset_id, spreadsheet_filename, is_csv=False, id_column='doc_id', content_column='doc_content'):
		dataset_path = '{}/data/{}'.format(request.folder, dataset_id)
		if not os.path.exists(dataset_path):
			os.makedirs(dataset_path)
		with Corpus_DB(path=dataset_path, isImport=True) as corpus_db:
			corpus_db.ImportFromSpreadsheet(spreadsheet_filename, is_csv=is_csv, id_key=id_column, content_key=content_column)

	return {}

def plaintext():
	def ImportPlaintext(dataset_id, plaintext_filename):
		dataset_path = '{}/data/{}'.format(request.folder, dataset_id)
		if not os.path.exists(dataset_path):
			os.makedirs(dataset_path)
		with Corpus_DB(path=dataset_path, isImport=True) as corpus_db:
			corpus_db.ImportFromFile(plaintext_filename)
	
	return {}
