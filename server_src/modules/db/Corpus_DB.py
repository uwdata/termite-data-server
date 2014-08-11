#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import re
from gluon.sql import DAL, Field
from utils.UnicodeIO import UnicodeReader, UnicodeWriter

class Corpus_DB():
	FILENAME = 'corpus.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	DOC_IDS = ['doc_id', 'docid']
	DOC_CONTENTS = ['doc_content', 'doccontent', 'docbody', 'doc_body']
	MODEL_KEY = 'corpus'
	MODEL_DESC = 'Text Corpus'
	MODEL_ENTRY = { 'model_key' : MODEL_KEY, 'model_desc' : MODEL_DESC }
	LINEBREAKS_TABS = re.compile(r'[\t\r\n\f]')
	
	DEFAULT_OPTIONS = {
		'token_regex' : r'\w{3,}',        # Tokenize a corpus into a bag-of-words language model
		'min_freq' : 5,                   # Number of times a term must appear in the corpus
		'min_doc_freq' : 3                # Number of documents in which a terms must appear
	}
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		if path is not None:
			self.db = DAL(Corpus_DB.CONNECTION, lazy_tables = not self.isInit, migrate_enabled = self.isInit, folder = path)
		else:
			self.db = DAL(Corpus_DB.CONNECTION, lazy_tables = not self.isInit, migrate_enabled = self.isInit)

	def __enter__(self):
		self.DefineOptionsTable()
		self.DefineModelsTable()
		self.DefineCorpusTable()
		self.DefineMetadataTables()
		return self

	def __exit__(self, type, value, traceback):
		self.DefineCorpusTextSearch()
		self.db.commit()
	
################################################################################
	
	def DefineOptionsTable(self):
		self.db.define_table( 'options',
			Field( 'key'  , 'string', required = True, unique = True ),
			Field( 'value', 'string', required = True ),
			migrate = self.isInit
		)
		for key, value in Corpus_DB.DEFAULT_OPTIONS.iteritems():
			self.SetOption( key, value, overwrite = self.isInit )
			
	
	def SetOption(self, key, value, overwrite = True):
		where = self.db.options.key == key
		if self.db( where ).count() > 0:
			if overwrite:
				self.db( where ).update( value = value )
		else:
			self.db.options.insert( key = key, value = value )
		self.db.commit()

	def GetOption(self, key):
		where = self.db.options.key == key
		keyValue = self.db( where ).select( self.db.options.value ).first()
		if keyValue:
			return keyValue.value
		else:
			return None

	def DefineModelsTable(self):
		self.db.define_table( 'models',
			Field( 'model_key' , 'string', required = True, unique = True ),
			Field( 'model_desc', 'string', required = True ),
			migrate = self.isInit
		)

	def AddModel(self, model_key, model_desc):
		where = self.db.models.model_key == model_key
		if self.db( where ).count() > 0:
			self.db( where ).update( model_desc = model_desc )
		else:
			self.db.models.insert( model_key = model_key, model_desc = model_desc )
		self.db.commit()
	
	def GetModel(self, model_key):
		if model_key == Corpus_DB.MODEL_KEY:
			return Corpus_DB.MODEL_ENTRY
		where = self.db.models.model_key == model_key
		keyValue = self.db( where ).select( self.db.models.ALL ).first()
		if keyValue:
			return { 'model_key' : keyValue.model_key, 'model_desc' : keyValue.model_desc }
		else:
			return None

	def GetModels(self):
		rows = self.db( self.db.models ).select( self.db.models.model_key, self.db.models.model_desc ).as_list()
		return [ Corpus_DB.MODEL_ENTRY ] + rows

################################################################################

	def DefineCorpusTable(self):
		self.db.define_table( 'corpus',
			Field( 'doc_index'  , 'integer', required = True, unique = True, default = -1 ),
			Field( 'doc_id'     , 'string' , required = True, unique = True ),
			Field( 'doc_content', 'text'   , required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS corpus_doc_index ON corpus (doc_index);' )
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS corpus_doc_id    ON corpus (doc_id);' )
	
	def DefineMetadataTables(self):
		self.db.define_table( 'fields',
			Field( 'field_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'field_name' , 'string' , required = True, unique = True ),
			Field( 'field_type' , 'string' , required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS field_index ON fields (field_index);' )
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS field_name  ON fields (field_name);'  )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS field_type  ON fields (field_type);'  )
		
		self.db.define_table( 'metadata',
			Field( 'doc_index'  , 'integer', required = True, default = -1 ),
			Field( 'field_index', 'integer', required = True, default = -1 ),
			Field( 'value'      , 'text'   , required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS metadata_indexes     ON metadata (doc_index, field_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS metadata_doc_index   ON metadata (doc_index);'              )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS metadata_field_index ON metadata (field_index);'            )

################################################################################

	def DefineCorpusTextSearch(self):
		if self.isInit:
			pass
#			self.db.executesql( 'DROP TABLE IF EXISTS corpus_search;' )
#			self.db.executesql( 'CREATE VIRTUAL TABLE corpus_search USING fts3 (doc_content TEXT);' )
#			self.db.executesql( 'INSERT INTO corpus_search (rowid, doc_content) SELECT doc_index, doc_content FROM corpus;' )
	
################################################################################

	def SanitizeText(self, text):
		text = Corpus_DB.LINEBREAKS_TABS.sub(u' ', text).strip()
		return text

	def ImportFromFile(self, filename):
		"""
		filename = A plain-text file (utf-8 encoded) containing one document per line
		"""
		def ReadFile():
			with open(filename, 'r') as f:
				for index, line in enumerate(f):
					doc_index = index
					values = line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
					if len(values) == 1:
						doc_id = 'doc{}'.format(doc_index+1)
						doc_content = values[0]
					else:
						doc_id = values[0]
						doc_content = values[1]
					yield {
						'doc_index' : doc_index,
						'doc_id' : doc_id,
						'doc_content' : doc_content.encode('utf-8', 'ignore')
					}
		self.db.corpus.bulk_insert(ReadFile())

	def ImportFromFolder(self, glob_pattern):
		"""
		glob_pattern = A folder of files or a glob pattern for list of files (utf-8 encoded, one document per file)
		"""
		def ReadFolder():
			filenames = sorted(glob.glob(glob_pattern))
			for index, filename in enumerate(filenames):
				doc_index = index
				doc_id = filename
				with open(filename, 'r') as f:
					doc_content = f.read().decode('utf-8', 'ignore')
					yield {
						'doc_index' : doc_index,
						'doc_id' : doc_id,
						'doc_content' : doc_content.encode('utf-8', 'ignore')
					}
		self.db.corpus.bulk_insert(ReadFolder())

	def ImportFromSpreadsheet(self, filename, id_key = None, content_key = None, is_csv = False):
		"""
		filename = A tab- or comman-separated spreadsheet (utf-8 encoded, with a header row containing column names)
		id_key = Name of the column containing unique document IDs
		content_key = Name of the column containing the document contents
		"""
		doc_id_keys = frozenset([id_key] if id_key is not None else Corpus_DB.DOC_IDS) 
		doc_content_keys = frozenset([content_key] if content_key is not None else Corpus_DB.DOC_CONTENTS)
		field_indexes = []
		field_names = []
		field_types = []
		metadata = []
		
		def ReadCSV():
			with open(filename, 'r') as f:
				reader = UnicodeReader(f)
				for row in reader:
					yield row

		def ReadTSV():
			with open(filename, 'r') as f:
				for line in f:
					yield line.decode('utf-8', 'ignore').rstrip('\n').split('\t')
					
		def ReadSpreadsheet(reader):
			field_doc_id = None
			field_doc_content = None
			for row_index, values in enumerate(reader):
				if row_index == 0:
					for index, field in enumerate(values):
						if field.lower() in doc_id_keys:
							field_doc_id = index
						elif field.lower() in doc_content_keys:
							field_doc_content = index
						else:
							field_index = len(field_indexes)
							field_indexes.append(field_index)
							field_names.append(field)
							field_types.append('integer')
				else:
					doc_index = row_index - 1
					doc_id = 'doc{:d}'.format(doc_index+1)
					doc_content = ''
					field_index = 0
					for index, value in enumerate(values):
						if field_doc_id == index:
							doc_id = value
						elif field_doc_content == index:
							doc_content = value
						else:
							metadata.append({
								'doc_index' : doc_index,
								'field_index' : field_index,
								'value' : value.encode('utf-8', 'ignore')
							})
						
							# [START] infer field type
							field_type = field_types[field_index]
							if field_type == 'integer':
								try:
									int(value)
								except ValueError:
									field_type = 'double'
							if field_type == 'double':
								try:
									float(value)
								except ValueError:
									field_type = 'string'
							field_types[field_index] = field_type
							# [END] infer field type
						
							field_index += 1
					yield {
						'doc_index' : doc_index,
						'doc_id' : doc_id,
						'doc_content' : doc_content.encode('utf-8', 'ignore')
					}

		def GetFields():
			for field_index in field_indexes:
				field_name = field_names[field_index]
				field_type = field_types[field_index]
				yield {
					'field_index' : field_index,
					'field_name' : field_name,
					'field_type' : field_type
				}
						
		reader = ReadCSV() if is_csv else ReadTSV()
		self.db.corpus.bulk_insert(ReadSpreadsheet(reader))
		self.db.fields.bulk_insert(GetFields())
		self.db.metadata.bulk_insert(metadata)
		
	def ExportToFile(self, filename):
		"""
		filename = A tab-delimited file (utf-8 encoded, without header) containing docIDs and document contents
		"""
		def WriteFile(rows):
			with open(filename, 'w') as f:
				for row in rows:
					doc_id = row.doc_id
					doc_content = self.SanitizeText(row.doc_content.decode('utf-8'))
					f.write(u'{}\t{}\n'.format(doc_id, doc_content).encode('utf-8', 'ignore'))

		rows = self.db().select(self.db.corpus.doc_id, self.db.corpus.doc_content, orderby = self.db.corpus.doc_index)
		WriteFile(rows)

	def ExportToSpreadsheet(self, filename, id_key = None, content_key = None, is_csv = False):
		"""
		filename = A tab- or comma-separated spreadsheet (utf-8 encoded, with header) containing the text corpus and all metadata
		"""
		field_names = [ row.field_name for row in self.db().select(self.db.fields.field_name, orderby = self.db.fields.field_index) ]
		field_count = len(field_names)
		all_field_names = [
			id_key if id_key is not None else 'doc_id',
			content_key if content_key is not None else 'doc_content'
		] + field_names

		def WriteCSV(rows):
			with open(filename, 'w') as f:
				writer = UnicodeWriter(f)
				writer.writerow(all_field_names)
				for row in rows:
					doc_index = row.doc_index
					doc_id = row.doc_id
					doc_content = self.SanitizeText(row.doc_content.decode('utf-8'))
					values = [u''] * field_count
					for d in self.db(self.db.metadata.doc_index == doc_index).select(self.db.metadata.field_index, self.db.metadata.value):
						values[d.field_index] = self.SanitizeText(d.value.decode('utf-8'))
					all_values = [ doc_id, doc_content ] + values
					writer.writerow(all_values)
			
		def WriteTSV(rows):
			with open(filename, 'w') as f:
				f.write(u'{}\n'.format(u'\t'.join(all_field_names)).encode('utf-8', 'ignore'))
				for row in rows:
					doc_index = row.doc_index
					doc_id = row.doc_id
					doc_content = self.SanitizeText(row.doc_content.decode('utf-8'))
					values = [u''] * field_count
					for d in self.db(self.db.metadata.doc_index == doc_index).select(self.db.metadata.field_index, self.db.metadata.value):
						values[d.field_index] = self.SanitizeText(d.value.decode('utf-8'))
					all_values = [ doc_id, doc_content ] + values
					f.write(u'{}\n'.format(u'\t'.join(all_values)).encode('utf-8', 'ignore'))

		rows = self.db().select(self.db.corpus.doc_index, self.db.corpus.doc_id, self.db.corpus.doc_content, orderby = self.db.corpus.doc_index)
		if is_csv:
			WriteCSV(rows)
		else:
			WriteTSV(rows)
