#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.Corpus_DB import Corpus_DB
from handlers.Corpus_Core import Corpus_Core

def index():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
	return handler.GenerateResponse()

def MetadataFields():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadMetadataFields()
	return handler.GenerateResponse()

def DocumentByIndex():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadDocumentByIndex()
	return handler.GenerateResponse()

def DocumentById():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadDocumentById()
	return handler.GenerateResponse()

def SearchDocuments():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.SearchDocuments()
	return handler.GenerateResponse()

def TextSearch():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTextSearch()
	return handler.GenerateResponse()

def TermFreqs():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTermFreqs()
	return handler.GenerateResponse()

def TermProbs():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTermProbs()
	return handler.GenerateResponse()

def TermCoFreqs():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTermCoFreqs()
	return handler.GenerateResponse()

def TermCoProbs():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTermCoProbs()
	return handler.GenerateResponse()

def TermPMI():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTermPMI()
	return handler.GenerateResponse()

def TermG2():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadTermG2()
	return handler.GenerateResponse()

def SentenceCoFreqs():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadSentenceCoFreqs()
	return handler.GenerateResponse()

def SentenceCoProbs():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadSentenceCoProbs()
	return handler.GenerateResponse()

def SentencePMI():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadSentencePMI()
	return handler.GenerateResponse()

def SentenceG2():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadSentenceG2()
	return handler.GenerateResponse()
