#!/usr/bin/env python

from handlers.Home_Core import Home_Core

def index():
	handler = Home_Core(request, response)
	return handler.GenerateResponse()
