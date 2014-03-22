#!/usr/bin/env python

import os
import json
from core import TermiteCore

class LDA( TermiteCore ):
	def __init__( self, request, response ):
		super( LDA, self ).__init__( request, response )
	
	def GetParam( self, key ):
		if key == 'docLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'docLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'docLimit', 5 )
			self.params.update({ key : value })
		
		if key == 'docOffset':
			value = self.GetNonNegativeIntegerParam( 'docOffset', 0 )
			self.params.update({ key : value })
		
		if key == 'termLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'termLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'termLimit', 5 )
			self.params.update({ key : value })

		if key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( 'termOffset', 0 )
			self.params.update({ key : value })

		if key == 'topicIndex':
			value = self.GetNonNegativeIntegerParam( 'topicIndex', 0 )
			self.params.update({ key : value })
			
		return value
	
	def LoadTermIndex( self ):
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			allTerms = json.load( f, encoding = 'utf-8' )
		termMaxCount = len(allTerms)
		subTerms = allTerms[termOffset:termOffset+termLimit]
		termCount = len(subTerms)
		for index, term in enumerate(subTerms):
			term['index'] = index
		results = {
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount,
			'TermIndex' : subTerms
		}
		self.content.update(results)
		return results

	def LoadDocIndex( self ):
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			allDocs = json.load( f, encoding = 'utf-8' )
		docMaxCount = len(allDocs)
		subDocs = allDocs[docOffset:docOffset+docLimit]
		docCount = len(subDocs)
		for index, doc in enumerate(subDocs):
			doc['index'] = index
		results = {
			'DocLimit' : docLimit,
			'DocOffset' : docOffset,
			'DocCount' : docCount,
			'DocMaxCount' : docMaxCount,
			'DocIndex' : subDocs
		}
		self.content.update(results)
		return results
	
	def LoadTopicIndex( self ):
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			allTopics = json.load( f, encoding = 'utf-8' )
		topicCount = len(allTopics)
		results = {
			'TopicCount' : topicCount,
			'TopicIndex' : allTopics
		}
		self.content.update(results)
		return results
	
	def LoadTermTopicMatrix( self ):
		self.LoadTermIndex()
		termSet = frozenset( d['text'] for d in self.content['TermIndex'] )
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = { term : matrix[term] for term in termSet }
		results = {
			'TermTopicMatrix' : submatrix
		}
		self.content.update(results)
		return results

	def LoadTopicTermMatrix( self ):
		self.LoadTermIndex()
		termSet = frozenset( d['text'] for d in self.content['TermIndex'] )
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = [ { term : vector[term] for term in termSet if term in vector } for vector in matrix ]
		results = {
			'TopicTermMatrix' : submatrix
		}
		self.content.update(results)
		return results
	
	def LoadDocTopicMatrix( self ):
		self.LoadDocIndex()
		docSet = frozenset( d['docID'] for d in self.content['DocIndex'] )
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = { doc : matrix[doc] for doc in docSet }
		results = {
			'DocTopicMatrix' : submatrix
		}
		self.content.update(results)
		return results
	
	def LoadTopicDocMatrix( self ):
		self.LoadDocIndex()
		docSet = frozenset( d['docID'] for d in self.content['DocIndex'] )
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-doc-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = [ { doc : vector[doc] for doc in docSet if doc in vector } for vector in matrix ]
		results = {
			'TopicDocMatrix' : submatrix
		}
		self.content.update(results)
		return results
		
	def LoadTopicCooccurrence( self ):
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-cooccurrence.json' )
		with open( filename ) as f:
			topicCooccurrence = json.load( f, encoding = 'utf-8' )
		results = {
			'TopicCooccurrence' : topicCooccurrence
		}
		self.content.update(results)
		return results

	def LoadTopicCovariance( self ):
		self.LoadTopicCooccurrence()
		topicCooccurrence = self.content['TopicCooccurrence']
		normalization = sum( [ sum( vector ) for vector in topicCooccurrence ] )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		topicCovariance = [ [ value * normalization for value in vector ] for vector in topicCooccurrence ]
		results = {
			'TopicCovariance' : topicCovariance
		}
		self.content.update(results)
		return results

	def LoadTopicTopTerms( self ):
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = []
		for vector in matrix:
			allTerms = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subTerms = allTerms[termOffset:termOffset+termLimit]
			termSet = frozenset(subTerms)
			submatrix.append( [ { term : vector[term] } for term in termSet if term in vector ] )
		results = {
			'TopicTopTerms' : submatrix
		}
		self.content.update(results)
		return results

	def LoadTopicTopDocs( self ):
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-doc-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = []
		for vector in matrix:
			allDocs = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subDocs = allDocs[docOffset:docOffset+docLimit]
			docSet = frozenset(subDocs)
			submatrix.append( [ { doc : vector[doc] } for doc in docSet if doc in vector ] )
		results = {
			'TopicTopDocs' : submatrix
		}
		self.content.update(results)
		return results
