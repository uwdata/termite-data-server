#!/usr/bin/env python

import os
import json

class LDA:
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
			'docLimit' : GetNonNegativeInteger( 'docLimit', 100 ),
			'docOffset' : GetNonNegativeInteger( 'docOffset', 0 ),
			'termLimit' : GetNonNegativeInteger( 'termLimit', 100 ),
			'termOffset' : GetNonNegativeInteger( 'termOffset', 0 )
		}
		return params
	
	def GetDocIndex( self, params = None ):
		if params is None:
			params = self.params
		docLimit = params['docLimit']
		docOffset = params['docOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			allDocs = json.load( f, encoding = 'utf-8' )
		docCount = len(allDocs)
		subDocs = allDocs[docOffset:docOffset+docLimit]
		return subDocs, docCount
	
	def GetTermIndex( self,	params = None ):
		if params is None:
			params = self.params
		termLimit = params['termLimit']
		termOffset = params['termOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			allTerms = json.load( f, encoding = 'utf-8' )
		termCount = len(allTerms)
		subTerms = allTerms[termOffset:termOffset+termLimit]
		return subTerms, termCount
	
	def GetTopicIndex( self, params = None ):
		if params is None:
			params = self.params
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			allTopics = json.load( f, encoding = 'utf-8' )
		topicCount = len(allTopics)
		return allTopics, topicCount
	
	def GetTermTopicMatrix( self, params = None ):
		if params is None:
			params = self.params
		termIndex, _ = self.GetTermIndex( params )
		topicIndex, _ = self.GetTopicIndex( params )
		termSet = frozenset( d['text'] for d in termIndex )
		topicSet = frozenset( d['index'] for d in topicIndex )
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		if type(matrix) == list:
			submatrix = { d['text'] : matrix[int(d['index'])] for d in termIndex }
		else:
			submatrix = { term : matrix[term] for term in termSet }
		return submatrix
	
	def GetDocTopicMatrix( self, params = None ):
		if params is None:
			params = self.params
		docIndex, _ = self.GetDocIndex( params )
		topicIndex, _ = self.GetTopicIndex( params )
		docSet = frozenset( d['docID'] for d in docIndex )
		topicSet = frozenset( d['index'] for d in topicIndex )
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		if type(matrix) == list:
			submatrix = { d['docID'] : matrix[int(d['index'])] for d in docIndex }
		else:
			submatrix = { doc : matrix[doc] for doc in docSet }
		return submatrix
	
	def GetTopicCooccurrence( self, params = None ):
		if params is None:
			params = self.params
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-cooccurrence.json' )
		with open( filename ) as f:
			allTopicCoFreqs = json.load( f, encoding = 'utf-8' )
		return allTopicCoFreqs
