#!/usr/bin/env python

from core.ITMCore import ITMCore
from db.LDA_DB import LDA_DB
from db.LDAStats_DB import LDAStats_DB

def index():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = ITMCore( request, response, lda_db, ldaStats_db )
	return core.GenerateResponse()

def Update():
	with LDA_DB() as lda_db:
		with LDAStats_DB() as ldaStats_db:
			core = ITMCore( request, response, lda_db, ldaStats_db )
			core.UpdateModel()
	return core.GenerateResponse()
