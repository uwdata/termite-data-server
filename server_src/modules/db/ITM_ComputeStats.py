#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class ITM_ComputeStats():

	def __init__(self, itm_db, corpus_db):
		self.logger = logging.getLogger('termite')
		self.db = itm_db.db
		self.itm_db = itm_db
		self.corpus_db = corpus_db

	def Execute(self):
		self.logger.info( 'Computing derived ITM statistics...' )
		self.corpus_db.AddModel('itm', 'Interactive topic modeling')
