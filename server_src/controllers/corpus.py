#!/usr/bin/env python

from core import TermiteCore
from corpus import Corpus

def index():
	core = TermiteCore( request, response )
	corpus = Corpus( request )
	params = corpus.GetParams()
	return core.GenerateResponse( params )

def DocMeta():
	core = TermiteCore( request, response )
	corpus = Corpus( request )
	params = corpus.GetParams()
	results = corpus.GetDocMeta( params )
	return core.GenerateResponse( params, results )
