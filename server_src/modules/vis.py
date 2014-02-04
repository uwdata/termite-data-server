#!/usr/bin/env python

import os
import json

class GroupInABox( LDA ):
	def __init__( self, request ):
		self.request = request
		self.params = self.GetParams()
	
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
