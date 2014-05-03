#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class ITM_ComputeStats():

	def __init__(self, itm_db, corpus_db):
		self.logger = logging.getLogger('termite')
		self.db = itm_db.db
		self.itmDB = itm_db
		self.corpusDB = corpus_db

################################################################################

	def Execute(self):
		self.logger.info( 'Computing derived ITM topic model statistics...' )
		self.corpusDB.AddModel('itm', 'Interactive Topic Model')
