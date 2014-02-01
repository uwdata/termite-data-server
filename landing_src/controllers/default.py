#!/usr/bin/env python

from core import TermiteCore

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()
