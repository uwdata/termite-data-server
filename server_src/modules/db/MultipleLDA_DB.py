#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class MultipleLDA_DB():
	FILENAME = 'multiple_lda.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	DEFAULT_OPTIONS = {
		'max_co_topic_count' : 10000       # Number of topic pairs to store
	}
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		if path is not None:
			self.db = DAL(MultipleLDA_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit, folder = path)
		else:
			self.db = DAL(MultipleLDA_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit)

	def __enter__(self):
		self.DefineOptionsTable()
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
		if self.isInit:
			for key, value in LDA_DB.DEFAULT_OPTIONS.iteritems():
				self.SetOption( key, value )

	def SetOption(self, key, value):
		where = self.db.options.key == key
		if self.db( where ).count() > 0:
			self.db( where ).update( value = value )
		else:
			self.db.options.insert( key = key, value = value )

	def GetOption(self, key):
		where = self.db.options.key == key
		keyValue = self.db( where ).select( self.db.options.value ).first()
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
			Field( 'entry_index', 'integer'     , required = True, default = -1 ),
			Field( 'topic_index', 'integer'     , required = True, default = -1 ),
			Field( 'topic_freq' , 'double'      , required = True ),
			Field( 'topic_label', 'string'      , required = True ),
			Field( 'topic_desc' , 'string'      , required = True ),
			Field( 'top_terms'  , 'list:integer', required = True ),
			Field( 'top_docs'   , 'list:integer', required = True ),
			Field( 'rank'       , 'integer'     , required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topics_indexes   ON topics (entry_index, topic_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_freq      ON topics (topic_freq);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_rank      ON topics (rank);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_freqEntry ON topics (entry_index, topic_freq);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS topics_rankEntry ON topics (entry_index, rank);' )

	def DefineMatrixTables(self):
		self.db.define_table( 'term_topic_matrix',
			Field( 'entry_index', 'integer', required = True, default = -1 ),
			Field( 'term_index' , 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_topic_indexes         ON term_topic_matrix (entry_index, term_index, topic_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_value           ON term_topic_matrix (value);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_rank            ON term_topic_matrix (rank);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_termindex       ON term_topic_matrix (term_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_topicindex      ON term_topic_matrix (topic_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_valueEntry      ON term_topic_matrix (entry_index, value);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_rankEntry       ON term_topic_matrix (entry_index, rank);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_termindexEntry  ON term_topic_matrix (entry_index, term_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS term_topic_topicindexEntry ON term_topic_matrix (entry_index, topic_index);' )
		
		self.db.define_table( 'doc_topic_matrix',
			Field( 'entry_index', 'integer', required = True, default = -1 ),
			Field( 'doc_index'  , 'integer', required = True, default = -1 ),
			Field( 'topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS doc_topic_indexes         ON doc_topic_matrix (entry_index, doc_index, topic_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_value           ON doc_topic_matrix (value);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_rank            ON doc_topic_matrix (rank);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_docindex        ON doc_topic_matrix (doc_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_topicindex      ON doc_topic_matrix (topic_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_valueEntry      ON doc_topic_matrix (entry_index, value);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_rankEntry       ON doc_topic_matrix (entry_index, rank);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_docindexEntry   ON doc_topic_matrix (entry_index, doc_index);' )
			self.db.executesql( 'CREATE        INDEX IF NOT EXISTS doc_topic_topicindexEntry ON doc_topic_matrix (entry_index, topic_index);' )

	def DefineStatsTables(self):
		self.db.define_table( 'topic_cossim',
			Field( 'first_entry_index' , 'integer', required = True, default = -1 ),
			Field( 'first_topic_index' , 'integer', required = True, default = -1 ),
			Field( 'second_entry_index', 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_cossim_indexes ON topic_cossim (first_entry_index, first_topic_index, second_entry_index, second_topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cossim_value       ON topic_cossim (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cossim_rank        ON topic_cossim (rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cossim_valueFirst  ON topic_cossim (first_entry_index, first_topic_index, value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cossim_rankFirst   ON topic_cossim (first_entry_index, first_topic_index, rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cossim_valueSecond ON topic_cossim (second_entry_index, second_topic_index, value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cossim_rankSecond  ON topic_cossim (second_entry_index, second_topic_index, rank);' )

		self.db.define_table( 'topic_kldiv',
			Field( 'first_entry_index' , 'integer', required = True, default = -1 ),
			Field( 'first_topic_index' , 'integer', required = True, default = -1 ),
			Field( 'second_entry_index', 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_kldiv_indexes ON topic_kldiv (first_entry_index, first_topic_index, second_entry_index, second_topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_kldiv_value       ON topic_kldiv (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_kldiv_rank        ON topic_kldiv (rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_kldiv_valueFirst  ON topic_kldiv (first_entry_index, first_topic_index, value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_kldiv_rankFirst   ON topic_kldiv (first_entry_index, first_topic_index, rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_kldiv_valueSecond ON topic_kldiv (second_entry_index, second_topic_index, value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_kldiv_rankSecond  ON topic_kldiv (second_entry_index, second_topic_index, rank);' )

		self.db.define_table( 'topic_rdp',
			Field( 'first_entry_index' , 'integer', required = True, default = -1 ),
			Field( 'first_topic_index' , 'integer', required = True, default = -1 ),
			Field( 'second_entry_index', 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			migrate = self.isInit
		)
		if self.isInit:
			self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_rdp_indexes ON topic_rdp (first_entry_index, first_topic_index, second_entry_index, second_topic_index);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_rdp_value       ON topic_rdp (value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_rdp_rank        ON topic_rdp (rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_rdp_valueFirst  ON topic_rdp (first_entry_index, first_topic_index, value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_rdp_rankFirst   ON topic_rdp (first_entry_index, first_topic_index, rank);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_rdp_valueSecond ON topic_rdp (second_entry_index, second_topic_index, value);' )
			self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_rdp_rankSecond  ON topic_rdp (second_entry_index, second_topic_index, rank);' )

################################################################################

	def Reset(self):
		self.db.executesql( 'DELETE FROM terms;' )
		self.db.executesql( 'DELETE FROM docs;' )
		self.db.executesql( 'DELETE FROM topics;' )
		self.db.executesql( 'DELETE FROM term_topic_matrix;' )
		self.db.executesql( 'DELETE FROM doc_topic_matrix;' )
		self.db.executesql( 'DELETE FROM topic_cossim;' )
		self.db.executesql( 'DELETE FROM topic_kldiv;' )
		self.db.executesql( 'DELETE FROM topic_rdp;' )
