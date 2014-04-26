#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class LDA_DB():
	FILENAME = 'lda.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		if path is not None:
			self.db = DAL( LDA_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit, folder = path )
		else:
			self.db = DAL( LDA_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit )

	def __enter__(self):
		self.DefineDimensionTables()
		self.DefineMatrixTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
	
	def DefineDimensionTables(self):
		self.db.define_table( 'terms',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'term_text' , 'string' , required = True, unique = True ),
			Field( 'term_freq' , 'double' , required = True ),
			Field( 'rank'      , 'integer', required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS terms_index ON terms (term_index);' )
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS terms_text  ON terms (term_text);' )
		self.db.executesql( 'CREATE        INDEX IF NOT EXISTS terms_freq  ON terms (term_freq);' )
		self.db.executesql( 'CREATE        INDEX IF NOT EXISTS terms_rank  ON terms (rank);' )
		self.db.define_table( 'docs',
			Field( 'doc_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'doc_id'   , 'string' , required = True, unique = True ),
			Field( 'doc_freq' , 'double' , required = True ),
			Field( 'rank'     , 'integer', required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS docs_index ON docs (doc_index);' )
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS docs_id    ON docs (doc_id);' )
		self.db.executesql( 'CREATE        INDEX IF NOT EXISTS docs_freq  ON docs (doc_freq);' )
		self.db.executesql( 'CREATE        INDEX IF NOT EXISTS docs_rank  ON docs (rank);' )
		self.db.define_table( 'topics',
			Field( 'topic_index', 'integer'     , required = True, unique = True, default = -1 ),
			Field( 'topic_freq' , 'double'      , required = True ),
			Field( 'topic_label', 'string'      , required = True ),
			Field( 'topic_desc' , 'string'      , required = True ),
			Field( 'top_terms'  , 'list:integer', required = True ),
			Field( 'top_docs'   , 'list:integer', required = True ),
			Field( 'rank'       , 'integer'     , required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topics_index ON topics (topic_index);' )
		self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_freq  ON topics (topic_freq);' )
		self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_rank  ON topics (rank);' )

	def DefineMatrixTables(self):
		self.db.define_table( 'term_topic_matrix',
			Field( 'term_index' , 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_topic_indexes ON term_topic_matrix (term_index, topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_value      ON term_topic_matrix (value);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_rank       ON term_topic_matrix (rank);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_termindex  ON term_topic_matrix (term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_topicindex ON term_topic_matrix (topic_index);' )
		
		self.db.define_table( 'doc_topic_matrix',
			Field( 'doc_index'  , 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS doc_topic_indexes ON doc_topic_matrix (doc_index, topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_value      ON doc_topic_matrix (value);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_rank       ON doc_topic_matrix (rank);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_docindex   ON doc_topic_matrix (doc_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_topicindex ON doc_topic_matrix (topic_index);' )
