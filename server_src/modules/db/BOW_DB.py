#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class BOW_DB():
	FILENAME = 'bow.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	DEFAULT_OPTIONS = {
		'max_freq_count' : 4000,          # Maximum number of terms to store
		'max_co_freq_count' : 100000      # Maximum number of term pairs to store
	}
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		if path is not None:
			self.db = DAL(BOW_DB.CONNECTION, lazy_tables = not self.isInit, migrate_enabled = self.isInit, folder = path)
		else:
			self.db = DAL(BOW_DB.CONNECTION, lazy_tables = not self.isInit, migrate_enabled = self.isInit)

	def __enter__(self):
		self.DefineOptionsTable()
		self.DefineTermStatsTables()
		self.DefineTermCoStatsTables()
		self.DefineSentenceCoStatsTables()
		self.DefineTemporaryTable()
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
		for key, value in BOW_DB.DEFAULT_OPTIONS.iteritems():
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
		self.db.executesql( 'DELETE FROM term_g2;' )
		self.db.executesql( 'DELETE FROM sentences_co_freqs;' )
		self.db.executesql( 'DELETE FROM sentences_co_probs;' )
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
