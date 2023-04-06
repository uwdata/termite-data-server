#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from db.BOW_DB import BOW_DB
from db.LDA_DB import LDA_DB
from vis.TermTopicMatrix1 import TermTopicMatrix1

def index():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix1(request, response, bow_db, lda_db)
	return handler.GenerateResponse()

def StateModel():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix1(request, response, bow_db, lda_db)
			data = handler.GetStateModel()
	dataStr = json.dumps(data, indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr

def SeriatedTermTopicProbabilityModel():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix1(request, response, bow_db, lda_db)
			data = handler.GetSeriatedTermTopicProbabilityModel()
	dataStr = json.dumps(data, indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr

def FilteredTermTopicProbabilityModel():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix1(request, response, bow_db, lda_db)
	data = handler.GetFilteredTermTopicProbabilityModel()
	dataStr = json.dumps(data, indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr

def TermFrequencyModel():
	with BOW_DB() as bow_db:
		with LDA_DB() as lda_db:
			handler = TermTopicMatrix1(request, response, bow_db, lda_db)
			data = handler.GetTermFrequencyModel()
	dataStr = json.dumps(data, indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr
