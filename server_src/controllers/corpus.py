#!/usr/bin/env python

from core.CorpusCore import CorpusCore
from db.Corpus_DB import Corpus_DB
from db.CorpusStats_DB import CorpusStats_DB

def index():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
	return core.GenerateResponse()

def MetadataFields():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadMetadataFields()
	return core.GenerateResponse()

def DocumentByIndex():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadDocumentByIndex()
	return core.GenerateResponse()

def DocumentById():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadDocumentById()
	return core.GenerateResponse()

def SearchDocuments():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.SearchDocuments()
	return core.GenerateResponse()

def TextSearch():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTextSearch()
	return core.GenerateResponse()

def TermFreqs():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTermFreqs()
	return core.GenerateResponse()

def TermProbs():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTermProbs()
	return core.GenerateResponse()

def TermCoFreqs():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTermCoFreqs()
	return core.GenerateResponse()

def TermCoProbs():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTermCoProbs()
	return core.GenerateResponse()

def TermPMI():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTermPMI()
	return core.GenerateResponse()

def TermG2():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadTermG2()
	return core.GenerateResponse()

def SentenceCoFreqs():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadSentenceCoFreqs()
	return core.GenerateResponse()

def SentenceCoProbs():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadSentenceCoProbs()
	return core.GenerateResponse()

def SentencePMI():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadSentencePMI()
	return core.GenerateResponse()

def SentenceG2():
	with Corpus_DB() as corpus_db:
		with CorpusStats_DB() as corpusStats_db:
			core = CorpusCore( request, response, corpus_db, corpusStats_db )
			core.LoadSentenceG2()
	return core.GenerateResponse()
