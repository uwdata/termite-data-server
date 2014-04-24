#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class Corpus_DB():
	FILENAME = 'corpus.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		self.isLazy = not isInit
		if path is not None:
			self.db = DAL( Corpus_DB.CONNECTION, lazy_tables = self.isLazy, folder = path )
		else:
			self.db = DAL( Corpus_DB.CONNECTION, lazy_tables = self.isLazy )
	
	def DefineTables(self):
		# create table if not exists fields (field_index integer primary key autoincrement, field_name text unique)
		self.db.define_table( 'fields',
			Field( 'field_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'field_name', 'integer', required = True ),
			redefine = False
		)
		
		# create table if not exists docs (doc_index integer primary key autoincrement, doc_id text unique)
		self.db.define_table( 'docs',
			Field( 'doc_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'doc_id', 'integer', required = True ),
			redefine = False
		)

		# create table if not exists corpus (rowid integer primary key autoincrement, doc_index integer, field_index integer, value blob)
		# create unique index if not exists doc_field on corpus (doc_index, field_index)
		self.db.define_table( 'corpus',
			Field( 'doc_index', 'integer', required = True, default = -1 ),
			Field( 'field_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'blob', required = True ),
			redefine = False
		)
		self.db.commit()
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS corpus_indexes ON corpus (doc_index, field_index);' )
	
	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
