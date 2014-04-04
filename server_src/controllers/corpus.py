#!/usr/bin/env python

from corpus import Corpus

def index():
	corpus = Corpus( request, response )
	return corpus.GenerateResponse()

def Document():
	corpus = Corpus( request, response )
	corpus.LoadDocument()
	return corpus.GenerateResponse()

def TextSearch():
	corpus = Corpus( request, response )
	corpus.LoadTextSearch()
	return corpus.GenerateResponse()

def TermFreqs():
	corpus = Corpus( request, response )
	corpus.LoadTermFreqs()
	return corpus.GenerateResponse()

def TermProbs():
	corpus = Corpus( request, response )
	corpus.LoadTermProbs()
	return corpus.GenerateResponse()

def TermCoFreqs():
	corpus = Corpus( request, response )
	corpus.LoadTermCoFreqs()
	return corpus.GenerateResponse()

def TermCoProbs():
	corpus = Corpus( request, response )
	corpus.LoadTermCoProbs()
	return corpus.GenerateResponse()

def TermPMI():
	corpus = Corpus( request, response )
	corpus.LoadTermPMI()
	return corpus.GenerateResponse()

def TermG2():
	corpus = Corpus( request, response )
	corpus.LoadTermG2()
	return corpus.GenerateResponse()

def TermSentencePMI():
	corpus = Corpus( request, response )
	corpus.LoadTermSentencePMI()
	return corpus.GenerateResponse()

def TermSentenceG2():
	corpus = Corpus( request, response )
	corpus.LoadTermSentenceG2()
	return corpus.GenerateResponse()
