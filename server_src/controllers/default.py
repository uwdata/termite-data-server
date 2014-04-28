#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers.Home_Core import Home_Core

def index():
	handler = Home_Core(request, response)
	return handler.GenerateResponse()
