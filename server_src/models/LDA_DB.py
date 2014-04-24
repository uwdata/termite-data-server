#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class LDA_DB():
	FILENAME = 'lda.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		self.isLazy = not isInit
		if path is not None:
			self.db = DAL( LDA_DB.CONNECTION, lazy_tables = self.isLazy, folder = path )
		else:
			self.db = DAL( LDA_DB.CONNECTION, lazy_tables = self.isLazy )
	
	def DefineTables(self):
		self.db.define_table( 'terms',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'term_text', 'string', required = True, unique = True ),
			redefine = False
		)
		self.db.define_table( 'docs',
			Field( 'doc_index', 'integer', required = True, unique = True, default = -1 ),
			redefine = False
		)
		self.db.define_table( 'topics',
			Field( 'topic_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'topic_freq', 'double', required = True ),
			Field( 'topic_desc', 'string', required = True ),
			Field( 'topic_top_terms', 'list:string', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topics_freq ON topics (topic_freq);' )
		
		self.db.define_table( 'term_topic_matrix',
			Field( 'term_index', 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_topic_indexes ON term_topic_matrix (term_index, topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_values     ON term_topic_matrix (value);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_termindex  ON term_topic_matrix (term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_topicindex ON term_topic_matrix (topic_index);' )
		
		self.db.define_table( 'doc_topic_matrix',
			Field( 'doc_index', 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS doc_topic_indexes ON doc_topic_matrix (doc_index, topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_values     ON doc_topic_matrix (value);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_docindex   ON doc_topic_matrix (doc_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_topicindex ON doc_topic_matrix (topic_index);' )
	
	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
