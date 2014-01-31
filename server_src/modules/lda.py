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
			'termLimit' : GetNonNegativeInteger( 'termLimit', 100 ),
			'topicLimit' : GetNonNegativeInteger( 'topicLimit', 50 ),
			'docOffset' : GetNonNegativeInteger( 'docOffset', 0 ),
			'termOffset' : GetNonNegativeInteger( 'termOffset', 0 ),
			'topicOffset' : GetNonNegativeInteger( 'topicOffset', 0 )
		}
		return params
	
	def GetDocIndex( self, params = None ):
		if params is None:
			params = self.params
		docLimit = params['docLimit']
		docOffset = params['docOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[docOffset:docOffset+docLimit]
		return content, maxCount
	
	def GetTermIndex( self,	params = None ):
		if params is None:
			params = self.params
		termLimit = params['termLimit']
		termOffset = params['termOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[termOffset:termOffset+termLimit]
		return content, maxCount
	
	def GetTopicIndex( self, params = None ):
		if params is None:
			params = self.params
		topicLimit = params['topicLimit']
		topicOffset = params['topicOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[topicOffset:topicOffset+topicLimit]
		return content, maxCount
	
	def GetTermTopicMatrix( self, params = None ):
		if params is None:
			params = self.params
		termIndex, _ = self.GetTermIndex( params )
		topicIndex, _ = self.GetTopicIndex( params )
		termSet = frozenset( d['text'] for d in termIndex )
		topicSet = frozenset( d['index'] for d in topicIndex )
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.txt' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		submatrix = {}
		for term in content:
			if term in termSet:
				submatrix[term] = {}
				for topic in content[term]:
					if topic in topicSet:
						submatrix[term][topic] = content[term][topic]
		return submatrix
	
	def GetDocTopicMatrix( self, params = None ):
		if params is None:
			params = self.params
		docIndex, _ = self.GetDocIndex( params )
		topicIndex, _ = self.GetTopicIndex( params )
		docSet = frozenset( d['docID'] for d in docIndex )
		topicSet = frozenset( d['index'] for d in topicIndex )
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.txt' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		submatrix = {}
		for docID in content:
			if docID in docSet:
				submatrix[docID] = {}
				for topic in content[docID]:
					if topic in topicSet:
						submatrix[docID][topic] = content[docID][topic]
		return submatrix