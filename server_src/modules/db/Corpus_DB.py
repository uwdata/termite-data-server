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
	DEFAULT_OPTIONS = {
		'token_regex' : r'\w{3,}',
		'min_freq' : 5,
		'min_doc_freq' : 3,
		'max_term_count' : 4000,
		'max_co_term_count' : 160000,
		'max_co_term_percentage' : 0.1
	}
	
	def __init__(self, path = None, isInit = False, isImport = False, isReset = False):
		self.isInit = isInit
		self.isImport = isImport
		self.isReset = isReset
		
		isInitOrImport = self.isInit or self.isImport
		if path is not None:
			self.db = DAL(Corpus_DB.CONNECTION, lazy_tables = not isInitOrImport, migrate_enabled = isInitOrImport, folder = path)
		else:
			self.db = DAL(Corpus_DB.CONNECTION, lazy_tables = not isInitOrImport, migrate_enabled = isInitOrImport)

	def __enter__(self):
		self.DefineOptionsTable()
		self.DefineModelsTable()
		self.DefineCorpusTable()
		self.DefineMetadataTables()
		if self.isReset:
			self.Reset()
		self.DefineTermStatsTables()
		self.DefineTermCoStatsTables()
		self.DefineSentenceCoStatsTables()
		self.DefineTemporaryTable()
		return self

	def __exit__(self, type, value, traceback):
		self.DefineCorpusTextSearch()
		self.db.commit()
	
################################################################################
	
	def DefineOptionsTable(self):
		self.db.define_table( 'options',
			Field( 'key'  , 'string', required = True, unique = True ),
			Field( 'value', 'string', required = True ),
			migrate = self.isImport
		)
		for key, value in Corpus_DB.DEFAULT_OPTIONS.iteritems():
			if self.db(self.db.options.key == key).count() == 0:
				self.db.options.insert(key = key, value = value)
	
	def SetOption(self, key, value):
		keyValue = self.db( self.db.options.key == key ).select().first()
		if keyValue:
			keyValue.update_record( value = value )
		else:
			self.db.options.insert( key = key, value = value )

	def GetOption(self, key):
		keyValue = self.db( self.db.options.key == key ).select( self.db.options.value ).first()
		if keyValue:
			return keyValue.value
		else:
			return None

	def DefineModelsTable(self):
		self.db.define_table( 'models',
			Field( 'model_key' , 'string', required = True, unique = True ),
			Field( 'model_desc', 'string', required = True ),
			migrate = self.isImport
		)

	def AddModel(self, model_key, model_desc):
		model = self.db( self.db.models.model_key == model_key ).select().first()
		if model:
			self.db.update_record( model_desc = model_desc )
		else:
			self.db.models.insert( model_key = model_key, model_desc = model_desc )

	def GetModels(self):
		models = self.db( self.db.models ).select( self.db.models.model_key )
		return [ model.model_key for model in models ]

	def GetModelDescription(self, model_key):
		model = self.db( self.db.models.model_key == model_key ).select().first()
		if model:
			return model.model_desc
		else:
			return None

################################################################################

	def DefineCorpusTable(self):
		self.db.define_table( 'corpus',
			Field( 'doc_index'  , 'integer', required = True, unique = True, default = -1 ),
			Field( 'doc_id'     , 'string' , required = True, unique = True ),
			Field( 'doc_content', 'text'   , required = True ),
			migrate = self.isImport
		)
		if self.isImport:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS corpus_doc_index ON corpus (doc_index);' )
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS corpus_doc_id    ON corpus (doc_id);' )
	
	def DefineMetadataTables(self):
		self.db.define_table( 'fields',
			Field( 'field_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'field_name' , 'string' , required = True, unique = True ),
			Field( 'field_type' , 'string' , required = True ),
			migrate = self.isImport
		)
		if self.isImport:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS field_index ON fields (field_index);' )
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS field_name  ON fields (field_name);'  )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS field_type  ON fields (field_type);'  )
		
		self.db.define_table( 'metadata',
			Field( 'doc_index'  , 'integer', required = True, default = -1 ),
			Field( 'field_index', 'integer', required = True, default = -1 ),
			Field( 'value'      , 'text'   , required = True ),
			migrate = self.isImport
		)
		if self.isImport:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS metadata_indexes     ON metadata (doc_index, field_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS metadata_doc_index   ON metadata (doc_index);'              )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS metadata_field_index ON metadata (field_index);'            )

################################################################################

	def DefineCorpusTextSearch(self):
		if self.isImport:
			self.db.executesql( 'DROP TABLE IF EXISTS corpus_search;' )
			self.db.executesql( 'CREATE VIRTUAL TABLE corpus_search USING fts3 (doc_content TEXT);' )
			self.db.executesql( 'INSERT INTO corpus_search (rowid, doc_content) SELECT doc_index, doc_content FROM corpus;' )
	
################################################################################

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
						'doc_content' : doc_content.encode('utf-8')
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
						'doc_content' : doc_content.encode('utf-8')
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
								'value' : value.encode('utf-8')
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
						'doc_content' : doc_content.encode('utf-8')
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
			m = re.compile(r'\s+')
			with open(filename, 'w') as f:
				for row in rows:
					doc_id = row.doc_id
					doc_content = m.sub(u' ', row.doc_content.decode('utf-8'))
					f.write(u'{}\t{}\n'.format(doc_id, doc_content).encode('utf-8'))

		rows = self.db().select(self.db.corpus.doc_id, self.db.corpus.doc_content, orderby = self.db.corpus.doc_index)
		WriteFile(rows)

	def ExportToSpreadsheet(self, filename, is_csv = False):
		"""
		filename = A tab- or comma-separated spreadsheet (utf-8 encoded, with header) containing the text corpus and all metadata
		"""
		field_names = [ row.field_name for row in self.db().select(self.db.fields.field_name, orderby = self.db.fields.field_index) ]
		field_count = len(field_names)
		all_field_names = [ 'doc_id', 'doc_content' ] + field_names

		def WriteCSV(rows):
			m = re.compile(r'\s+')
			with open(filename, 'w') as f:
				writer = UnicodeWriter(f)
				writer.writerow(all_field_names)
				for row in rows:
					doc_index = row.doc_index
					doc_id = row.doc_id
					doc_content = m.sub(u' ', row.doc_content.decode('utf-8'))
					values = [u''] * field_count
					for d in self.db(self.db.metadata.doc_index == doc_index).select(self.db.metadata.field_index, self.db.metadata.value):
						values[d.field_index] = m.sub(u' ', d.value.decode('utf-8'))
					all_values = [ doc_id, doc_content ] + values
					writer.writerow(all_values)
			
		def WriteTSV(rows):
			m = re.compile(r'\s+')
			with open(filename, 'w') as f:
				f.write(u'{}\n'.format(u'\t'.join(all_field_names)).encode('utf-8'))
				for row in rows:
					doc_index = row.doc_index
					doc_id = row.doc_id
					doc_content = m.sub(u' ', row.doc_content.decode('utf-8'))
					values = [u''] * field_count
					for d in self.db(self.db.metadata.doc_index == doc_index).select(self.db.metadata.field_index, self.db.metadata.value):
						values[d.field_index] = m.sub(u' ', d.value.decode('utf-8'))
					all_values = [ doc_id, doc_content ] + values
					f.write(u'{}\n'.format(u'\t'.join(all_values)).encode('utf-8'))

		rows = self.db().select(self.db.corpus.doc_index, self.db.corpus.doc_id, self.db.corpus.doc_content, orderby = self.db.corpus.doc_index)
		if is_csv:
			WriteCSV(rows)
		else:
			WriteTSV(rows)

################################################################################

	def DefineTermStatsTables(self):
		self.db.define_table( 'term_texts',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'term_text' , 'string' , required = True, unique = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_text_value ON term_texts (term_text);' )
	
		self.db.define_table( 'term_freqs',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_freqs_value ON term_freqs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_freqs_rank ON term_freqs (rank);' )
	
		self.db.define_table( 'term_probs',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_probs_value ON term_probs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_probs_rank ON term_probs (rank);' )
	
		self.db.define_table( 'term_doc_freqs',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_doc_freqs_value ON term_doc_freqs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_doc_freqs_rank ON term_doc_freqs (rank);' )

	def DefineTermCoStatsTables(self):
		self.db.define_table( 'term_co_freqs',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_co_freqs_indexes ON term_co_freqs (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_freqs_value ON term_co_freqs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_freqs_rank ON term_co_freqs (rank);' )

		self.db.define_table( 'term_co_probs',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_co_probs_indexes ON term_co_probs (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_probs_value ON term_co_probs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_probs_rank ON term_co_probs (rank);' )

		self.db.define_table( 'term_pmi',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_pmi_indexes ON term_pmi (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_pmi_value ON term_pmi (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_pmi_rank ON term_pmi (rank);' )

		self.db.define_table( 'term_g2',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_g2_indexes ON term_g2 (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_g2_value ON term_g2 (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_g2_rank ON term_g2 (rank);' )

	def DefineSentenceCoStatsTables(self):
		self.db.define_table( 'sentences_co_freqs',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_co_freqs_indexes ON sentences_co_freqs (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_co_freqs_value ON sentences_co_freqs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_co_freqs_rank ON sentences_co_freqs (rank);' )

		self.db.define_table( 'sentences_co_probs',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_co_probs_indexes ON sentences_co_probs (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_co_probs_value ON sentences_co_probs (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_co_probs_rank ON sentences_co_probs (rank);' )

		self.db.define_table( 'sentences_pmi',
			Field( 'first_term_index' , 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_pmi_indexes ON sentences_pmi (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_pmi_value ON sentences_pmi (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_pmi_rank ON sentences_pmi (rank);' )

		self.db.define_table( 'sentences_g2',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_g2_indexes ON sentences_g2 (first_term_index, second_term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_g2_value ON sentences_g2 (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_g2_rank ON sentences_g2 (rank);' )

################################################################################

	def Reset(self):
		self.db.executesql( 'DELETE FROM term_texts;' )
		self.db.executesql( 'DELETE FROM term_freqs;' )
		self.db.executesql( 'DELETE FROM term_probs;' )
		self.db.executesql( 'DELETE FROM term_doc_freqs;' )
		self.db.executesql( 'DELETE FROM term_co_freqs;' )
		self.db.executesql( 'DELETE FROM term_co_probs;' )
		self.db.executesql( 'DELETE FROM term_pmi;' )
		self.db.executesql( 'DELETE FROM term_g2;' )
		self.db.executesql( 'DELETE FROM sentences_co_freqs;' )
		self.db.executesql( 'DELETE FROM sentences_co_probs;' )
		self.db.executesql( 'DELETE FROM sentences_pmi;' )
		self.db.executesql( 'DELETE FROM sentences_g2;' )

################################################################################

	def DefineTemporaryTable(self):
		self.db.define_table( 'vocab',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'term_text', 'string', required = True ),
			migrate = self.isInit
		)
		self.db.define_table( 'vocab_text',
			Field( 'term_text', 'string', required = True, unique = True, default = -1 ),
			migrate = self.isInit
		)
