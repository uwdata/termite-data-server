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
			core.LoadTermIndex()
	return core.GenerateResponse()

def DocIndex():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadDocIndex()
	return core.GenerateResponse()

def TopicIndex():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopicIndex()
	return core.GenerateResponse()

def TermTopicMatrix():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTermIndex()
			core.LoadTopicIndex()
			core.LoadTermTopicMatrix()
	return core.GenerateResponse()

def DocTopicMatrix():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadDocIndex()
			core.LoadTopicIndex()
			core.LoadDocTopicMatrix()
	return core.GenerateResponse()

def TopicCooccurrence():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopicIndex()
			core.LoadTopicCooccurrence()
	return core.GenerateResponse()

def TopicCovariance():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = LDACore( request, response, lda_db, ldaStats_db )
			core.LoadTopicIndex()
			core.LoadTopicCovariance()
	return core.GenerateResponse()
