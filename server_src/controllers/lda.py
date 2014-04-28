#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.Corpus_DB import Corpus_DB
from db.LDA_DB import LDA_DB
from handlers.LDA_Core import LDA_Core

def index():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
	return handler.GenerateResponse()

def TermIndex():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTerms()
	return handler.GenerateResponse()

def DocIndex():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadDocs()
	return handler.GenerateResponse()

def TopicIndex():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTopics()
	return handler.GenerateResponse()

def TermTopicMatrix():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTermTopicMatrix()
	return handler.GenerateResponse()

def DocTopicMatrix():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadDocTopicMatrix()
	return handler.GenerateResponse()

def TopicCooccurrences():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTopicCooccurrences()
	return handler.GenerateResponse()

def TopicCovariance():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTopicCovariance()
	return handler.GenerateResponse()

def TopTerms():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTopTerms()
	return handler.GenerateResponse()

def TopDocs():
	with LDA_DB() as lda_db:
		handler = LDA_Core(request, response, lda_db)
		handler.LoadTopDocs()
	return handler.GenerateResponse()
