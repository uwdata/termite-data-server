#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers.Home_Core import Home_Core

class ITM_Core(Home_Core):
	def __init__(self, request, response, itm_db):
		super(ITM_Core, self).__init__(request, response)
		self.itmDB = itm_db
		self.db = itm_db.db
