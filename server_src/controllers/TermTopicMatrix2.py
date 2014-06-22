#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from db.BOW_DB import BOW_DB
from db.LDA_DB import LDA_DB
from vis.TermTopicMatrix2 import TermTopicMatrix2

def index():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix2(request, response, bow_db, lda_db)
	return handler.GenerateResponse()

def GetEntry():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix2(request, response, bow_db, lda_db)
			data = handler.GetEntry()
	dataStr = json.dumps(data, encoding='utf-8', indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr
