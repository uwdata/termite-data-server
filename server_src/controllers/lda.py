#!/usr/bin/env python

from core.LDACore import LDACore
from db.LDA_DB import LDA_DB
from db.LDAStats_DB import LDAStats_DB

def index():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
	return core.GenerateResponse()

def TermIndex():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTerms()
	return core.GenerateResponse()

def DocIndex():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadDocs()
	return core.GenerateResponse()

def TopicIndex():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopics()
	return core.GenerateResponse()

def TermTopicMatrix():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTermTopicMatrix()
	return core.GenerateResponse()

def DocTopicMatrix():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadDocTopicMatrix()
	return core.GenerateResponse()

def TopicCooccurrences():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopicCooccurrences()
	return core.GenerateResponse()

def TopicCovariance():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopicCovariance()
	return core.GenerateResponse()

def TopTerms():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopTerms()
	return core.GenerateResponse()

def TopDocs():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopDocs()
	return core.GenerateResponse()
