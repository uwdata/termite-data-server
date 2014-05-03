#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class ITM_DB():
	FILENAME = 'itm.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	DEFAULT_OPTIONS = {}
	
	def __init__(self, path = None, isInit = False):
		self.isInit = isInit
		if path is not None:
			self.db = DAL(ITM_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit, folder = path)
		else:
			self.db = DAL(ITM_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit)

	def __enter__(self):
		self.DefineOptionsTable()
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
		for key, value in ITM_DB.DEFAULT_OPTIONS.iteritems():
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

	def Reset(self):
		pass