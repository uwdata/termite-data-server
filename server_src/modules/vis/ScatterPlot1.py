#!/usr/bin/env python

import os
import json
from json import encoder as JsonEncoder
from db.Corpus_DB import Corpus_DB
from db.LDA_DB import LDA_DB
from db.LDA_ComputeStats import LDA_ComputeStats
from handlers.Home_Core import Home_Core
from modellers.TreeTM import RefineLDA, InspectLDA
from readers.TreeTMReader import TreeTMReader

class ScatterPlot1(Home_Core):
	def __init__(self, request, response, corpus_db, bow_db, lda_db):
		super(ScatterPlot1, self).__init__(request, response)
		JsonEncoder.FLOAT_REPR = lambda number : format(number, '.4g')
		self.corpusDB = corpus_db
		self.bowDB = bow_db
		self.ldaDB = lda_db
		self.bow = bow_db.db
		self.db = lda_db.db
