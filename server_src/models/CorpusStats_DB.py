#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class CorpusStats_DB():
	FILENAME = 'corpus_stats.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, forceCommit = False):
		self.forceCommit = forceCommit
		self.lazyTables = not forceCommit
		if path is not None:
			self.db = DAL( CorpusStats_DB.CONNECTION, lazy_tables = self.lazyTables, folder = path )
		else:
			self.db = DAL( CorpusStats_DB.CONNECTION, lazy_tables = self.lazyTables )
	
	def DefineTables(self):
		self.db.define_table( 'term_stats',
			Field( 'term_index', 'integer', required = True, unique = True ),
			Field( 'term_text', 'string', required = True, unique = True ),
			Field( 'term_freq', 'double' ),
			Field( 'term_prob', 'double' ),
			Field( 'term_doc_freq', 'double' ),
			Field( 'term_idf', 'double' ),
			Field( 'term_tfidf', 'double' )
		)
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_stats_freq ON term_stats (term_freq);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_stats_prob ON term_stats (term_prob);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_stats_tfidf ON term_stats (term_tfidf);' )
		
		self.db.define_table( 'term_co_freqs',
			Field( 'first_term_index', 'integer', required = True ),
			Field( 'second_term_index', 'integer', required = True ),
			Field( 'value', 'double' ),
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_co_freqs_indexes ON term_co_freqs (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_freqs_value ON term_co_freqs (value);' )

		self.db.define_table( 'term_co_probs',
			Field( 'first_term_index', 'integer', required = True ),
			Field( 'second_term_index', 'integer', required = True ),
			Field( 'value', 'double' ),
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_co_probs_indexes ON term_co_probs (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_co_probs_value ON term_co_probs (value);' )
	
		self.db.define_table( 'term_pmi',
			Field( 'first_term_index', 'integer', required = True ),
			Field( 'second_term_index', 'integer', required = True ),
			Field( 'value', 'double' ),
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_pmi_indexes ON term_pmi (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_pmi_value ON term_pmi (value);' )
	
		self.db.define_table( 'term_g2',
			Field( 'first_term_index', 'integer', required = True ),
			Field( 'second_term_index', 'integer', required = True ),
			Field( 'value', 'double' ),
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS term_g2_indexes ON term_g2 (first_term_index, second_term_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS term_g2_value ON term_g2 (value);' )

	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
