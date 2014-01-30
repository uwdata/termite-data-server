#!/usr/bin/env python

import os
import json

class LDA:
	def __init__( self, request ):
		self.request = request
		
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

	def GetDocIndex( self, params ):
		docLimit = params['docLimit']
		docOffset = params['docOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[docOffset:docOffset+docLimit]
		return content, maxCount

	def GetTermIndex( self, params ):
		termLimit = params['termLimit']
		termOffset = params['termOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[termOffset:termOffset+termLimit]
		return content, maxCount

	def GetTopicIndex( self, params ):
		topicLimit = params['topicLimit']
		topicOffset = params['topicOffset']
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = content[topicOffset:topicOffset+topicLimit]
		return content, maxCount

	def GetTermTopicMatrix( self, params ):
		termLimit = params['termLimit']
		termOffset = params['termOffset']
		topicLimit = params['topicLimit']
		topicOffset = params['topicOffset']
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

	def GetDocTopicMatrix( self, params ):
		docLimit = params['docLimit']
		docOffset = params['docOffset']
		topicLimit = params['topicLimit']
		topicOffset = params['topicOffset']
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
