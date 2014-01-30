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
