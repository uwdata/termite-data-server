#!/usr/bin/env python

import os
import json
from handlers import Home_Core

class LDA_CovariateChart(Home_Core):
	def __init__(self, request, response):
		super(LDA_CovariateChart, self).__init__(request, response)

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

	def LoadDocIndex( self ):
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			allDocs = json.load( f, encoding = 'utf-8' )
		docMaxCount = len(allDocs)
		subDocs = allDocs[docOffset:docOffset+docLimit]
		docCount = len(subDocs)
		results = {
			'DocLimit' : docLimit,
			'DocOffset' : docOffset,
			'DocCount' : docCount,
			'DocMaxCount' : docMaxCount,
			'DocIndex' : subDocs
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
