#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class LDA_DB():
	FILENAME = 'lda.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	DEFAULT_OPTIONS = {
		'max_co_topic_count' : 40000
	}
	
	def __init__(self, path = None, isInit = False, isReset = False):
		self.isInit = isInit
		self.isReset = isReset
		
		if path is not None:
			self.db = DAL(LDA_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit, folder = path)
		else:
			self.db = DAL(LDA_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit)

	def __enter__(self):
		self.DefineOptionsTable()
		if self.isReset:
			self.Reset()
		self.DefineDimensionTables()
		self.DefineMatrixTables()
		self.DefineStatsTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
	
################################################################################

	def DefineOptionsTable(self):
		self.db.define_table( 'options',
			Field( 'key'  , 'string', required = True, unique = True ),
			Field( 'value', 'string', required = True ),
			migrate = self.isInit
		)
		if self.db(self.db.options).count() == 0:
			for key, value in LDA_DB.DEFAULT_OPTIONS.iteritems():
				self.db.options.insert( key = key, value = value )

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

################################################################################

	def DefineDimensionTables(self):
		self.db.define_table( 'terms',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'term_text' , 'string' , required = True, unique = True ),
			Field( 'term_freq' , 'double' , required = True ),
			Field( 'rank'      , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS terms_index ON terms (term_index);' )
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS terms_text  ON terms (term_text);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS terms_freq  ON terms (term_freq);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS terms_rank  ON terms (rank);' )
			
		self.db.define_table( 'docs',
			Field( 'doc_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'doc_id'   , 'string' , required = True, unique = True ),
			Field( 'doc_freq' , 'double' , required = True ),
			Field( 'rank'     , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
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
			Field( 'rank'       , 'integer'     , required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topics_index ON topics (topic_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_freq  ON topics (topic_freq);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_rank  ON topics (rank);' )

	def DefineMatrixTables(self):
		self.db.define_table( 'term_topic_matrix',
			Field( 'term_index' , 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_topic_indexes ON term_topic_matrix (term_index, topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_value      ON term_topic_matrix (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_rank       ON term_topic_matrix (rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_termindex  ON term_topic_matrix (term_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_topic_topicindex ON term_topic_matrix (topic_index);' )
		
		self.db.define_table( 'doc_topic_matrix',
			Field( 'doc_index'  , 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS doc_topic_indexes ON doc_topic_matrix (doc_index, topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_value      ON doc_topic_matrix (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_rank       ON doc_topic_matrix (rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_docindex   ON doc_topic_matrix (doc_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS doc_topic_topicindex ON doc_topic_matrix (topic_index);' )

	def DefineStatsTables(self):
		self.db.define_table( 'topic_cooccurrences',
			Field( 'first_topic_index' , 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_cooccurrences_indexes ON topic_cooccurrences (first_topic_index, second_topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cooccurrences_value ON topic_cooccurrences (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cooccurrences_rank ON topic_cooccurrences (rank);' )

		self.db.define_table( 'topic_covariance',
			Field( 'first_topic_index', 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_covariance_indexes ON topic_covariance (first_topic_index, second_topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_covariance_value ON topic_covariance (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_covariance_rank ON topic_covariance (rank);' )

################################################################################

	def Reset(self):
		self.db.executesql( 'DELETE FROM terms;' )
		self.db.executesql( 'DELETE FROM docs;' )
		self.db.executesql( 'DELETE FROM topics;' )
		self.db.executesql( 'DELETE FROM term_topic_matrix;' )
		self.db.executesql( 'DELETE FROM doc_topic_matrix;' )
		self.db.executesql( 'DELETE FROM topic_cooccurrences;' )
		self.db.executesql( 'DELETE FROM topic_covariance;' )

