#!/usr/bin/env python

from core.LDACore import LDACore
from db.LDA_DB import LDA_DB

def index():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
	return core.GenerateResponse()

def TermIndex():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTerms()
	return core.GenerateResponse()

def DocIndex():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadDocs()
	return core.GenerateResponse()

def TopicIndex():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTopics()
	return core.GenerateResponse()

def TermTopicMatrix():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTermTopicMatrix()
	return core.GenerateResponse()

def DocTopicMatrix():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadDocTopicMatrix()
	return core.GenerateResponse()

def TopicCooccurrences():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTopicCooccurrences()
	return core.GenerateResponse()

def TopicCovariance():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTopicCovariance()
	return core.GenerateResponse()

def TopTerms():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTopTerms()
	return core.GenerateResponse()

def TopDocs():
	with LDA_DB() as lda_db:
		core = LDACore(request, response, lda_db)
		core.LoadTopDocs()
	return core.GenerateResponse()
