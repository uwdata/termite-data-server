#!/usr/bin/env python

import os
import json

class GroupBox:
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
			'termLimit' : GetNonNegativeInteger( 'termLimit', 100 ),
			'termOffset' : GetNonNegativeInteger( 'termOffset', 0 ),
			'topicLimit' : GetNonNegativeInteger( 'topicLimit', 100 ),
			'topicOffset' : GetNonNegativeInteger( 'topicOffset', 0 )
		}
		return params
	
	def GetTermIndex( self ):
		termLimit = self.params['termLimit']
		termOffset = self.params['termOffset']
		filename = os.path.join( self.request.folder, 'data/group_box', 'term-index.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
		maxCount = len(content)
		content = sorted( content, key = lambda x : -x['freq'] )
		content = content[termOffset:termOffset+termLimit]
		return content, maxCount
	
	def GetTopicIndex( self ):
		topicLimit = self.params['topicLimit']
		topicOffset = self.params['topicOffset']
		filename = os.path.join( self.request.folder, 'data/group_box', 'topic-index.json' )
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
		filename = os.path.join( self.request.folder, 'data/group_box', 'term-topic-matrix.txt' )
		content = []
		with open( filename ) as f:
			for termIndex, line in enumerate( f ):
				if termOffset <= termIndex < termOffset+termLimit:
					values = [ float(value) for value in line[:-1].split('\t') ]
					content.append( values[topicOffset:topicOffset+topicLimit] )
				if termIndex > termOffset+termLimit:
					break
		return content

	def GetTermCooccurrence( self ):
		termLimit = self.params['termLimit']
		termOffset = self.params['termOffset']
		filename = os.path.join( self.request.folder, 'data/group_box', 'term-index.json' )
		with open( filename ) as f:
			terms = json.load( f, encoding = 'utf-8' )
		maxCount = len(terms)
		terms = sorted( terms, key = lambda x : -x['freq'] )
		terms = terms[termOffset:termOffset+termLimit]
		terms = frozenset( term['text'] for term in terms )
		
		filename = os.path.join( self.request.folder, 'data/group_box', 'term-cooccurrence.json' )
		with open( filename, 'r' ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
			
		matrix = { firstTerm : { secondTerm : value for secondTerm, value in secondTermAndValue.iteritems() if secondTerm in terms } for firstTerm, secondTermAndValue in matrix.iteritems()	 if firstTerm in terms }
		return matrix
		
	def GetTopicCooccurrence( self ):
		filename = os.path.join( self.request.folder, 'data/group_box', 'topic-cooccurrence.json' )
		with open( filename, 'r' ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		return matrix
