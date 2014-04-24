#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class CorpusStats_DB():
	FILENAME = 'corpus_stats.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		self.isLazy = not isInit
		if path is not None:
			self.db = DAL( CorpusStats_DB.CONNECTION, lazy_tables = self.isLazy, folder = path )
		else:
			self.db = DAL( CorpusStats_DB.CONNECTION, lazy_tables = self.isLazy )
	
	def DefineTables(self):
		self.db.define_table( 'term_texts',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'term_text', 'string', required = True, unique = True ),
			redefine = False
		)
		
		self.db.define_table( 'term_freqs',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_freqs_value ON term_freqs (value);' )
		
		self.db.define_table( 'term_probs',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_probs_value ON term_probs (value);' )
		
		self.db.define_table( 'term_doc_freqs',
			Field( 'term_index', 'integer', required = True, unique = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_doc_freqs_value ON term_doc_freqs (value);' )
		
		self.db.define_table( 'term_co_freqs',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_co_freqs_indexes ON term_co_freqs (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_freqs_value ON term_co_freqs (value);' )

		self.db.define_table( 'term_co_probs',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_co_probs_indexes ON term_co_probs (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_probs_value ON term_co_probs (value);' )
	
		self.db.define_table( 'term_pmi',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_pmi_indexes ON term_pmi (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_pmi_value ON term_pmi (value);' )
	
		self.db.define_table( 'term_g2',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_g2_indexes ON term_g2 (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_g2_value ON term_g2 (value);' )

		self.db.define_table( 'sentences_co_freqs',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_co_freqs_indexes ON sentences_co_freqs (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_co_freqs_value ON sentences_co_freqs (value);' )

		self.db.define_table( 'sentences_co_probs',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_co_probs_indexes ON sentences_co_probs (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_co_probs_value ON sentences_co_probs (value);' )
	
		self.db.define_table( 'sentences_pmi',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_pmi_indexes ON sentences_pmi (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_pmi_value ON sentences_pmi (value);' )
	
		self.db.define_table( 'sentences_g2',
			Field( 'first_term_index', 'integer', required = True, default = -1 ),
			Field( 'second_term_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS sentences_g2_indexes ON sentences_g2 (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS sentences_g2_value ON sentences_g2 (value);' )

	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
