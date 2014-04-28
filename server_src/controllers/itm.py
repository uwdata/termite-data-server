#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.Corpus_DB import Corpus_DB
from db.LDA_DB import LDA_DB
from handlers.ITM_Core import ITM_Core
from handlers.ITM_GroupInBox import ITM_GroupInBox

def index():
	with LDA_DB() as lda_db:
		handler = ITM_Core( request, response, lda_db )
	return handler.GenerateResponse()

def Update():
	with LDA_DB() as lda_db:
		handler = ITM_Core( request, response, lda_db )
		handler.UpdateModel()
	return handler.GenerateResponse()

def gib():
	with Corpus_DB() as corpus_db:
		with LDA_DB() as lda_db:
			gib = ITM_GroupInBox(request, response, corpus_db, lda_db)
	gib.Load()
	return gib.GenerateResponse()
