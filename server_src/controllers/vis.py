#!/usr/bin/env python

from core.HomeCore import HomeCore
from core.GroupInABox import GroupInABox as GroupInABoxModel
from db.Corpus_DB import Corpus_DB
from db.LDA_DB import LDA_DB

def index():
	core = HomeCore(request, response)
	return core.GenerateResponse()

def GroupInABox():
	with Corpus_DB() as corpus_db:
		with LDA_DB() as lda_db:
			gib = GroupInABoxModel(request, response, corpus_db, lda_db)
	gib.Load()
	return gib.GenerateResponse()
