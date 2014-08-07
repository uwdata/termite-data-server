#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.Corpus_DB import Corpus_DB
from handlers.Corpus_Core import Corpus_Core

def index():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
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

def LoadDocuments():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadDocuments()
	return handler.GenerateResponse()

def SearchDocuments():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.SearchDocuments()
	return handler.GenerateResponse()

def MetadataFields():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadMetadataFields()
	return handler.GenerateResponse()

def MetadataByName():
	with Corpus_DB() as corpus_db:
		handler = Corpus_Core(request, response, corpus_db)
		handler.LoadMetadataByName()
	return handler.GenerateResponse()
