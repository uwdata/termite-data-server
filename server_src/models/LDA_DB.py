#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field
from gluon.validators import *

class LDA_DB():
	FILENAME = 'lda.db'
	
	def __init__(self, path = None):
		if path is not None:
			self.db = DAL( 'sqlite://{}'.format(LDA_DB.FILENAME), folder = path )
		else:
			self.db = DAL( 'sqlite://{}'.format(LDA_DB.FILENAME) )
	
	def DefineTables(self):
		self.db.define_table( 'terms',
			Field( 'term_index', 'integer', required = True, unique = True ),
			Field( 'text', 'string', required = True, unique = True )
		)
		self.db.define_table( 'docs',
			Field( 'doc_index', 'integer', required = True, unique = True )
		)
		self.db.define_table( 'topics',
			Field( 'topic_index', 'integer', required = True, unique = True ),
			Field( 'freq', 'double' ),
			Field( 'desc', 'string' ),
			Field( 'top_terms', 'list:string' )
		)
		self.db.define_table( 'term_topic_matrix',
			Field( 'term_index', 'integer', required = True ),
			Field( 'topic_index', 'integer', required = True ),
			Field( 'value', 'double', required = True )
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_index1 ON term_topic_matrix (term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_index2 ON term_topic_matrix (topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_indexes ON term_topic_matrix (term_index, topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_values  ON term_topic_matrix (value);' )
		
		self.db.define_table( 'doc_topic_matrix',
			Field( 'doc_index', 'integer', required = True ),
			Field( 'topic_index', 'integer', required = True ),
			Field( 'value', 'double', required = True )
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_index1 ON doc_topic_matrix (doc_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_index2 ON doc_topic_matrix (topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_indexes ON doc_topic_matrix (doc_index, topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_values  ON doc_topic_matrix (value);' )
	
	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
