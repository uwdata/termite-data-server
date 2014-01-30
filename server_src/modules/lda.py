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
	
	def GetDocIndex( self ):
		docLimit = self.params['docLimit']
		docOffset = self.params['docOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[docOffset:docOffset+docLimit]
		return content, maxCount
	
	def GetTermIndex( self ):
		termLimit = self.params['termLimit']
		termOffset = self.params['termOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[termOffset:termOffset+termLimit]
		return content, maxCount
	
	def GetTopicIndex( self ):
		topicLimit = self.params['topicLimit']
		topicOffset = self.params['topicOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[topicOffset:topicOffset+topicLimit]
		return content, maxCount
	
	def GetTermTopicMatrix( self ):
		termLimit = self.params['termLimit']
		termOffset = self.params['termOffset']
		topicLimit = self.params['topicLimit']
		topicOffset = self.params['topicOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.txt' )
		content = []
		with open( filename ) as f:
			for termIndex, line in enumerate( f ):
				if termOffset <= termIndex < termOffset+termLimit:
					values = [ float(value) for value in line[:-1].split('\t') ]
					content.append( values[topicOffset:topicOffset+topicLimit] )
				if termIndex > termOffset+termLimit:
					break
		return content
	
	def GetDocTopicMatrix( self ):
		docLimit = self.params['docLimit']
		docOffset = self.params['docOffset']
		topicLimit = self.params['topicLimit']
		topicOffset = self.params['topicOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.txt' )
		content = []
		with open( filename ) as f:
			for docIndex, line in enumerate( f ):
				if docOffset <= docIndex < docOffset+docLimit:
					values = [ float(value) for value in line[:-1].split('\t') ]
					content.append( values[topicOffset:topicOffset+topicLimit] )
				if docIndex > docOffset+docLimit:
					break
		return content
