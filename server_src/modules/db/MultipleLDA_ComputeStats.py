#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class MultipleLDA_ComputeStats():

	def __init__(self, lda_db, corpus_db):
		self.logger = logging.getLogger('termite')
		self.db = lda_db.db
		self.ldaDB = lda_db
		self.corpusDB = corpus_db
		
		self.maxCoTopicCount = int(self.ldaDB.GetOption('max_co_topic_count'))

################################################################################

	def Execute(self):
		self.logger.info( 'Computing derived LDA topic model statistics...' )
		self.logger.info( '    max_co_topic_count = %s', self.maxCoTopicCount )
		self.corpusDB.AddModel('ldas', 'Collection of Topic Models')
