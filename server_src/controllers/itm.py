#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.Corpus_DB import Corpus_DB
from db.BOW_DB import BOW_DB
from db.LDA_DB import LDA_DB
from db.ITM_DB import ITM_DB
from handlers.ITM_Core import ITM_Core
from vis.GroupInBox import GroupInBox as GroupInBoxHandler

def index():
	with ITM_DB() as itm_db:
		handler = ITM_Core(request, response, itm_db)
	return handler.GenerateResponse()

def Update():
	with Corpus_DB() as corpus_db:
		with BOW_DB() as bow_db:
			with LDA_DB() as lda_db:
				handler = GroupInBoxHandler(request, response, corpus_db, bow_db, lda_db)
	handler.UpdateModel()
	handler.InspectModel()
	return handler.GenerateResponse()

def Inspect():
	with Corpus_DB() as corpus_db:
		with BOW_DB() as bow_db:
			with LDA_DB() as lda_db:
				handler = GroupInBoxHandler(request, response, corpus_db, bow_db, lda_db)
	handler.InspectModel()
	return handler.GenerateResponse()

def GroupInBox():
	with Corpus_DB() as corpus_db:
		with BOW_DB() as bow_db:
			with LDA_DB() as lda_db:
				handler = GroupInBoxHandler(request, response, corpus_db, bow_db, lda_db)
	handler.LoadGIB()
	return handler.GenerateResponse()

def gib():
	with Corpus_DB() as corpus_db:
		with BOW_DB() as bow_db:
			with LDA_DB() as lda_db:
				handler = GroupInBoxHandler(request, response, corpus_db, bow_db, lda_db)
	handler.UpdateModel()
	handler.InspectModel()
	handler.LoadGIB()
	return handler.GenerateResponse()
