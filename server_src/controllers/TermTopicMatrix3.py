#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from db.BOW_DB import BOW_DB
from db.LDA_DB import LDA_DB
from vis.TermTopicMatrix3 import TermTopicMatrix3

def index():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix3(request, response, bow_db, lda_db)
	return handler.GenerateResponse()

def GetTerms():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix3(request, response, bow_db, lda_db)
			data = handler.GetTerms()
	dataStr = json.dumps(data, encoding='utf-8', indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr

def GetTopics():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix3(request, response, bow_db, lda_db)
			data = handler.GetTopics()
	dataStr = json.dumps(data, encoding='utf-8', indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr

def GetTermTopicMatrix():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix3(request, response, bow_db, lda_db)
			data = handler.GetTermTopicMatrix()
	dataStr = json.dumps(data, encoding='utf-8', indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr
