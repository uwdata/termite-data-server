#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class LDAStats_DB():
	FILENAME = 'lda_stats.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		self.isLazy = not isInit
		if path is not None:
			self.db = DAL( LDAStats_DB.CONNECTION, lazy_tables = self.isLazy, folder = path )
		else:
			self.db = DAL( LDAStats_DB.CONNECTION, lazy_tables = self.isLazy )
	
	def DefineTables(self):
		self.db.define_table( 'topic_cooccurrences',
			Field( 'first_topic_index' , 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_cooccurrences_indexes ON topic_cooccurrences (first_topic_index, second_topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cooccurrences_value ON topic_cooccurrences (value);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_cooccurrences_rank ON topic_cooccurrences (rank);' )

		self.db.define_table( 'topic_covariance',
			Field( 'first_topic_index', 'integer', required = True, default = -1 ),
			Field( 'second_topic_index', 'integer', required = True, default = -1 ),
			Field( 'value', 'double' , required = True ),
			Field( 'rank' , 'integer', required = True ),
			redefine = False
		)
		self.db.executesql( 'CREATE UNIQUE INDEX IF NOT EXISTS topic_covariance_indexes ON topic_covariance (first_topic_index, second_topic_index);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_covariance_value ON topic_covariance (value);' )
		self.db.executesql( 'CREATE INDEX IF NOT EXISTS topic_covariance_rank ON topic_covariance (rank);' )
	
	def __enter__(self):
		self.DefineTables()
		return self
	
	def __exit__(self, type, value, traceback):
		self.db.commit()
