#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.BOW_DB import BOW_DB
from handlers.BOW_Core import BOW_Core

def index():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
	return handler.GenerateResponse()

def TermFreqs():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadTermFreqs()
	return handler.GenerateResponse()

def TermProbs():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadTermProbs()
	return handler.GenerateResponse()

def TermCoFreqs():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadTermCoFreqs()
	return handler.GenerateResponse()

def TermCoProbs():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadTermCoProbs()
	return handler.GenerateResponse()

def TermG2():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadTermG2()
	return handler.GenerateResponse()

def SentenceCoFreqs():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadSentenceCoFreqs()
	return handler.GenerateResponse()

def SentenceCoProbs():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadSentenceCoProbs()
	return handler.GenerateResponse()

def SentenceG2():
	with BOW_DB() as bow_db:
		handler = BOW_Core(request, response, bow_db)
		handler.LoadSentenceG2()
	return handler.GenerateResponse()
