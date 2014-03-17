#!/usr/bin/env python

import os
import json
import operator

class CovariateChart:
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
			'termLimit' : GetNonNegativeInteger( 'termLimit', 5 ),
			'docLimit' : GetNonNegativeInteger( 'docLimit', 100 ),
			'topicIndex' : GetNonNegativeInteger( 'topicIndex', 0 )
		}
		return params

	def GetDocIndex( self, params = None ):
		if params is None:
			params = self.params
		docLimit = params['docLimit']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			allDocs = json.load( f, encoding = 'utf-8' )
		docCount = len(allDocs)
		subDocs = allDocs[:docLimit]
		return subDocs, docCount

	def GetTermIndex( self,	params = None ):
		if params is None:
			params = self.params
#		termLimit = params['termLimit']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			allTerms = json.load( f, encoding = 'utf-8' )
		termCount = len(allTerms)
		return allTerms, termCount
#		subTerms = allTerms[:termLimit]
#		return subTerms, termCount

	def GetDocTopics( self, params = None ):
		if params is None:
			params = self.params
		docIndex, _ = self.GetDocIndex( params )
		docSet = frozenset( d['docID'] for d in docIndex )
		topicIndex = params['topicIndex']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.txt' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		if type(matrix) == list:
			submatrix = { d['docID'] : matrix[int(d['index'])][topicIndex] for d in docIndex }
		else:
			submatrix = { doc : matrix[doc][topicIndex] for doc in docSet }
		return submatrix

	def GetTopTerms( self, params = None ):
		if params is None:
			params = self.params
		termLimit = params['termLimit']
		termIndex, _ = self.GetTermIndex( params )
		termSet = frozenset( d['text'] for d in termIndex )
		topicIndex = params['topicIndex']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.txt' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		if type(matrix) == list:
			submatrix = { d['text'] : matrix[int(d['index'])-1][topicIndex] for d in termIndex }
		else:
			submatrix = { term : matrix[term][topicIndex] for term in termSet }
		subterms = sorted( submatrix.iteritems(), key = operator.itemgetter(1) )
		subterms = subterms[-termLimit:]
		subterms.reverse()
		return subterms
