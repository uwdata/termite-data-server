#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.Corpus_DB import Corpus_DB
from db.LDA_DB import LDA_DB
from handlers.ITM_GroupInBox import ITM_GroupInBox

def index():
	with Corpus_DB() as corpus_db:
		with LDA_DB() as lda_db:
			gib = ITM_GroupInBox(request, response, corpus_db, lda_db)
	return gib.GenerateResponse()

def Update():
	with Corpus_DB() as corpus_db:
		with LDA_DB() as lda_db:
			gib = ITM_GroupInBox(request, response, corpus_db, lda_db)
	gib.UpdateModel()
	gib.InspectModel()
	return gib.GenerateResponse()

def Inspect():
	with Corpus_DB() as corpus_db:
		with LDA_DB() as lda_db:
			gib = ITM_GroupInBox(request, response, corpus_db, lda_db)
	gib.InspectModel()
	return gib.GenerateResponse()

def gib():
	with Corpus_DB() as corpus_db:
		with LDA_DB() as lda_db:
			gib = ITM_GroupInBox(request, response, corpus_db, lda_db)
	gib.UpdateModel()
	gib.InspectModel()
	gib.LoadGIB()
	return gib.GenerateResponse()
