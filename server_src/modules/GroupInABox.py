#!/usr/bin/env python

import os
import json
import operator

class GroupInABox:
	def __init__( self, request ):
		self.request = request
		self.params = self.GetParams()
	
	def GetParams( self ):
		def GetNonNegativeInteger( key, defaultValue ):
			try:
				n = int( self.request.vars[ key ] )
				if n >= 0:
					return n
				else:
					return 0
			except:
				return defaultValue
		
		params = {
			'termLimit' : GetNonNegativeInteger( 'termLimit', 100 )
		}
		return params
	
	def GetTopTermsPerTopic( self, params = None ):
		if params is None:
			params = self.params
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.txt' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		termLimit = params['termLimit']
		submatrix = []
		for topic in matrix:
			terms = sorted( topic.keys(), key = lambda x : -topic[x] )
			subtopic = [ { term : topic[term] } for term in terms[:termLimit] ]
			submatrix.append( subtopic )
		return submatrix

