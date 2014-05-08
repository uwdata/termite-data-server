#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from db.Corpus_DB import Corpus_DB
from db.BOW_DB import BOW_DB
from db.LDA_DB import LDA_DB
from db.ITM_DB import ITM_DB
from vis.GroupInBox import GroupInBox as GroupInBoxHandler

def index():
	with Corpus_DB() as corpus_db:
		with BOW_DB() as bow_db:
			with LDA_DB() as lda_db:
				handler = GroupInBoxHandler(request, response, corpus_db, bow_db, lda_db)
	response.delimiters = ('[[', ']]')
	return handler.GenerateResponse()

def gib():
	with Corpus_DB() as corpus_db:
		with BOW_DB() as bow_db:
			with LDA_DB() as lda_db:
				handler = GroupInBoxHandler(request, response, corpus_db, bow_db, lda_db)
	handler.UpdateModel()
	handler.InspectModel()
	handler.LoadGIB()
	dataStr = json.dumps(handler.content, encoding='utf-8', indent=2, sort_keys=True)
	response.headers['Content-Type'] = 'application/json'
	return dataStr
