#!/usr/bin/env python

import json
from db.LDA_DB import LDA_DB
from db.LDA_ComputeStats import LDA_ComputeStats
from handlers.Home_Core import Home_Core
from modellers.TreeTM import RefineLDA
from readers.TreeTMReader import TreeTMReader

class ITM_Core(Home_Core):
	def __init__(self, request, response, lda_db):
		super(ITM_Core, self).__init__(request, response)
		self.db = lda_db.db

	def GetAction(self):
		action = self.GetStringParam( 'action' )
		self.params.update({
			'action' : action
		})
		return action

	def GetIterCount(self, app_model_path):
		filename = '{}/index.json'.format(app_model_path)
		with open(filename, 'r') as f:
			data = json.load(f, encoding='utf-8')
			entry = data['completedEntryID']
		filename = '{}/entry-{:06d}/states.json'.format(app_model_path, entry)
		with open(filename, 'r') as f:
			data = json.load(f, encoding='utf-8')
			iterCount = data['numIters']
		return iterCount

	def GetIters(self, iterCount):
		iters = self.GetNonNegativeIntegerParam( 'iters', None )
		self.params.update({
			'iters' : iters if iters is not None else iterCount
		})
		return iters

	def GetConstraints(self):
		mustLinksStr = self.GetStringParam( 'mustLinks' )
		cannotLinksStr = self.GetStringParam( 'cannotLinks' )
		keepTermsStr = self.GetStringParam( 'keepTerms' )
		removeTermsStr =  self.GetStringParam( 'removeTerms' )
		mustLinks = []
		cannotLinks = []
		keepTerms = {}
		removeTerms = []
		try:
			data = json.loads(mustLinksStr)
			if type(data) is list:
				mustLinks = [ [ d for d in dd if type(d) is unicode ] for dd in data if type(dd) is list ]
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(cannotLinksStr)
			if type(data) is list:
				cannotLinks = [ [ d for d in dd if type(d) is unicode ] for dd in data if type(dd) is list ]
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(keepTermsStr)
			if type(data) is dict:
				for key, value in data.iteritems():
					keepTerms = { int(key) : [ d for d in value if type(d) is unicode ] for key, value in data.iteritems() if type(value) is list }
		except (ValueError, KeyError, TypeError):
			pass
		try:
			data = json.loads(removeTermsStr)
			if type(data) is list:
				removeTerms = [ d for d in data if type(d) is unicode ]
		except (ValueError, KeyError, TypeError):
			pass

		self.params.update({
			'mustLinks' : mustLinksStr,
			'cannotLinks' : cannotLinksStr,
			'keepTerms' : keepTermsStr,
			'removeTerms' : removeTermsStr
		})
		return mustLinks, cannotLinks, keepTerms, removeTerms

	def UpdateModel(self):
		app_path = self.request.folder
		app_model_path = '{}/data/treetm'.format(app_path)
		iterCount = self.GetIterCount(app_model_path)
		iters = self.GetIters(iterCount)
		mustLinks, cannotLinks, keepTerms, removeTerms = self.GetConstraints()
		action = self.GetAction()
		if action != 'train' or iters is None:
			self.content.update({
				'IterCount' : iterCount,
				'MustLinks' : mustLinks,
				'CannotLinks' : cannotLinks,
				'KeepTerms' : keepTerms,
				'RemoveTerms' : removeTerms
			})
		else:
			RefineLDA( app_model_path, numIters = iters, 
				mustLinks = mustLinks, cannotLinks = cannotLinks, keepTerms = keepTerms, removeTerms = removeTerms )
			with LDA_DB( isReset = True ) as lda_db:
				reader = TreeTMReader( lda_db, app_model_path )
				reader.Execute()
				computer = LDA_ComputeStats( lda_db )
				computer.Execute()
			self.content.update({
				'IterCount' : iterCount,
				'MustLinks' : mustLinks,
				'CannotLinks' : cannotLinks,
				'KeepTerms' : keepTerms,
				'RemoveTerms' : removeTerms
			})
