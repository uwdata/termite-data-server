#!/usr/bin/env python

from corpus import Corpus

def index():
	corpus = Corpus( request, response )
	return corpus.GenerateResponse()

def DocMeta():
	corpus = Corpus( request, response )
	corpus.LoadDocMeta()
	return corpus.GenerateResponse()

def TermFreqs():
	corpus = Corpus( request, response )
	corpus.LoadTermFreqs()
	return corpus.GenerateResponse()

def TermCoFreqs():
	corpus = Corpus( request, response )
	corpus.LoadTermCoFreqs()
	return corpus.GenerateResponse()

def TermProbs():
	corpus = Corpus( request, response )
	corpus.LoadTermProbs()
	return corpus.GenerateResponse()

def TermCoProbs():
	corpus = Corpus( request, response )
	corpus.LoadTermCoProbs()
	return corpus.GenerateResponse()

def TermPMI():
	corpus = Corpus( request, response )
	corpus.LoadTermPMI()
	return corpus.GenerateResponse()
