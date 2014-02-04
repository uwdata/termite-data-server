#!/usr/bin/env python

from core import TermiteCore
from corpus import Corpus

def index():
	core = TermiteCore( request, response )
	corpus = Corpus( request )
	return core.GenerateResponse( corpus.params )

def DocMeta():
	core = TermiteCore( request, response )
	corpus = Corpus( request )
	results = corpus.GetDocMeta()
	return core.GenerateResponse( corpus.params, results )

def TermFreqs():
	core = TermiteCore( request, response )
	corpus = Corpus( request )
	termFreqs = corpus.GetTermFreqs()
	return core.GenerateResponse( corpus.params, {
		'TermFreqs' : termFreqs
	})

def TermCoFreqs():
	core = TermiteCore( request, response )
	corpus = Corpus( request )
	termCoFreqs = corpus.GetTermCoFreqs()
	return core.GenerateResponse( corpus.params, {
		'TermCoFreqs' : termCoFreqs
	})
