#!/usr/bin/env python

from core.ITMCore import ITMCore
from db.LDA_DB import LDA_DB

def index():
	with LDA_DB() as lda_db:
		core = ITMCore( request, response, lda_db )
	return core.GenerateResponse()

def Update():
	with LDA_DB() as lda_db:
		core = ITMCore( request, response, lda_db )
		core.UpdateModel()
	return core.GenerateResponse()
