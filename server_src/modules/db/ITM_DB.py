#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gluon.sql import DAL, Field

class ITM_DB():
	FILENAME = 'itm.db'
	CONNECTION = 'sqlite://{}'.format(FILENAME)
	
	def __init__(self, path = None, isInit = False, isReset = False):
		self.isInit = isInit
		self.isReset = isReset
		
		if path is not None:
			self.db = DAL(ITM_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit, folder = path)
		else:
			self.db = DAL(ITM_DB.CONNECTION, lazy_tables = not self.isInit, migrate = self.isInit)

	def __enter__(self):
		self.DefineOptionsTable()
		if self.isReset:
			self.Reset()
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
			for key, value in ITM_DB.DEFAULT_OPTIONS.iteritems():
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

	def Reset(self):
		pass