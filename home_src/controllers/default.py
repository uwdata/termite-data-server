#!/usr/bin/env python

from core.HomeCore import HomeCore

def index():
	core = HomeCore(request, response)
	return core.GenerateResponse()
