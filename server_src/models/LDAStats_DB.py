#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class LDAStats_DB():
	FILENAME = 'lda_stats.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, forceCommit = False):
		self.forceCommit = forceCommit
		self.lazyTables = not forceCommit
		if path is not None:
			self.db = DAL( LDAStats_DB.CONNECTION, lazy_tables = self.lazyTables, folder = path )
		else:
			self.db = DAL( LDAStats_DB.CONNECTION, lazy_tables = self.lazyTables )
	
	def DefineTables(self):
		self.db.define_table( 'topic_cooccurrences',
			Field( 'first_topic_index', 'integer', required = True ),
			Field( 'second_topic_index', 'integer', required = True ),
			Field( 'value', 'double', required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_cooccurrences_indexes ON topic_cooccurrences (first_topic_index, second_topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cooccurrences_value ON topic_cooccurrences (value);' )

		self.db.define_table( 'topic_covariance',
			Field( 'first_topic_index', 'integer', required = True ),
			Field( 'second_topic_index', 'integer', required = True ),
			Field( 'value', 'double', required = True )
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_covariance_indexes ON topic_covariance (first_topic_index, second_topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_covariance_value ON topic_covariance (value);' )
	
	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
