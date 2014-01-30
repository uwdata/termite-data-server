#!/usr/bin/env python

from core import TermiteCore
from treetm import TreeTM

def index():
	core = TermiteCore( request, response )
	treetm = TreeTM( request )
	return core.GenerateResponse( treetm.params )

def TermTopicConstraints():
	core = TermiteCore( request, response )
	treetm = TreeTM( request )
	return core.GenerateResponse( treetm.params )
