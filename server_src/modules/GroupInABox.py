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
			'termLimit' : GetNonNegativeInteger( 'termLimit', 5 )
		}
		return params

	def GetTopicCooccurrence( self ):
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-cooccurrence.json' )
		with open( filename ) as f:
			allTopicCoFreqs = json.load( f, encoding = 'utf-8' )
		return allTopicCoFreqs
	
	def GetTopTermsPerTopic( self, params = None ):
		if params is None:
			params = self.params
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.txt' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		termLimit = params['termLimit']
		submatrix = []
		termSet = set()
		for topic in matrix:
			terms = sorted( topic.keys(), key = lambda x : -topic[x] )[:termLimit]
			termSet.update( terms )
			subtopic = [ { term : topic[term] } for term in terms ]
			submatrix.append( subtopic )
		return submatrix, termSet

	def GetTermCoFreqs( self, termSet ):
		filename = os.path.join( self.request.folder, 'data/corpus', 'term-co-freqs.json' )
		with open( filename ) as f:
			allTermCoFreqs = json.load( f, encoding = 'utf-8' )
		termCoFreqs = { term : allTermCoFreqs[term] for term in termSet if term in allTermCoFreqs }
		for term, termFreqs in termCoFreqs.iteritems():
			termCoFreqs[ term ] = { t : termFreqs[t] for t in termSet if t in termFreqs }
		return termCoFreqs
