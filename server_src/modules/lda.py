#!/usr/bin/env python

import os
import json
from core import TermiteCore

class LDA( TermiteCore ):
	def __init__( self, request, response ):
		super( LDA, self ).__init__( request, response )
	
	def GetParam( self, key ):
		if key == 'docOffset':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		if key == 'docLimit':
			if self.IsMachineFormat():
				value = self.GetNonNegativeIntegerParam( key, 100 )
			else:
				value = self.GetNonNegativeIntegerParam( key, 5 )
			self.params.update({ key : value })
		
		if key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		if key == 'termLimit':
			if self.IsMachineFormat():
				value = self.GetNonNegativeIntegerParam( key, 100 )
			else:
				value = self.GetNonNegativeIntegerParam( key, 5 )
			self.params.update({ key : value })
		
		if key == 'topicIndex':
			value = self.GetNonNegativeIntegerParam( key, None )
			self.params.update({ key : value })
		
		if key == 'threshold':
			value = self.GetNonNegativeFloatParam( key, 0 )
			self.params.update({ key : value })
			
		return value
	
	def LoadTermIndex( self ):
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		
		# Load from Disk
		filename = os.path.join( self.request.folder, 'data/lda', 'term-index.json' )
		with open( filename ) as f:
			allTerms = json.load( f, encoding = 'utf-8' )
		termMaxCount = len(allTerms)
		subTerms = allTerms[termOffset:termOffset+termLimit]
		termCount = len(subTerms)
		table = [ { 'index' : index, 'text' : term['text'] } for index, term in enumerate(subTerms) ]
		
		# Responses
		results = {
			'TermIndex' : table,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermMaxCount' : termMaxCount,
			'TermCount' : termCount
		}
		self.content.update(results)
		return results

	def LoadDocIndex( self ):
		# Parameters
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			allDocs = json.load( f, encoding = 'utf-8' )
		docMaxCount = len(allDocs)
		subDocs = allDocs[docOffset:docOffset+docLimit]
		docCount = len(subDocs)
		table = [ { 'index' : index, 'docID' : doc['docID'] } for index, doc in enumerate(subDocs) ]

		# Responses
		results = {
			'DocIndex' : table,
			'DocLimit' : docLimit,
			'DocOffset' : docOffset,
			'DocMaxCount' : docMaxCount,
			'DocCount' : docCount
		}
		self.content.update(results)
		return results
	
	def LoadTopicIndex( self ):
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			allTopics = json.load( f, encoding = 'utf-8' )
		topicCount = len(allTopics)
		table = [ { 'index' : index, 'name' : 'Topic #{}'.format(topic['index']+1) } for index, topic in enumerate(allTopics) ]

		# Responses
		results = {
			'TopicIndex' : table,
			'TopicCount' : topicCount
		}
		self.content.update(results)
		return results
	
	def LoadTermTopicMatrix( self ):
		# Parameters
		self.LoadTermIndex()
		termSet = frozenset( d['text'] for d in self.content['TermIndex'] )
		threshold = self.GetParam('threshold')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		table = []
		for term in termSet:
			table += [ { 'term' : term, 'topic' : index, 'value' : value } for index, value in enumerate(matrix[term]) if value > threshold ]
		table.sort( key = lambda x : -x['value'] )

		# Responses
		results = {
			'TermTopicMatrix' : table
		}
		self.content.update(results)
		return results

	def LoadTopicTermMatrix( self ):
		# Parameters
		self.LoadTermIndex()
		termSet = frozenset( d['text'] for d in self.content['TermIndex'] )
		threshold = self.GetParam('threshold')

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		table = []
		for index, vector in enumerate(matrix):
			table += [ { 'term' : term, 'topic' : index, 'value' : vector[term] } for term in termSet if term in vector ]
		table.sort( key = lambda x : -x['value'] )

		results = {
			'TopicTermMatrix' : table
		}
		self.content.update(results)
		return results
	
	def LoadDocTopicMatrix( self ):
		# Parameters
		self.LoadDocIndex()
		docSet = frozenset( d['docID'] for d in self.content['DocIndex'] )
		threshold = self.GetParam('threshold')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		table = []
		for docID in docSet:
			table += [ { 'docID' : docID, 'topic' : index, 'value' : value } for index, value in enumerate(matrix[docID]) if value > threshold ]
		table.sort( key = lambda x : -x['value'] )
		
		# Responses
		results = {
			'DocTopicMatrix' : table
		}
		self.content.update(results)
		return results
	
	def LoadTopicDocMatrix( self ):
		# Parameters
		self.LoadDocIndex()
		docSet = frozenset( d['docID'] for d in self.content['DocIndex'] )
		threshold = self.GetParam('threshold')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-doc-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		table = []
		for index, vector in enumerate(matrix):
			table += [ { 'docID' : docID, 'topic' : index, 'value' : vector[docID] } for docID in docSet if docID in vector ]
		table.sort( key = lambda x : -x['value'] )

		# Responses
		results = {
			'TopicDocMatrix' : table
		}
		self.content.update(results)
		return results
		
	def LoadTopicCooccurrence( self ):
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-cooccurrence.json' )
		with open( filename ) as f:
			topicCooccurrence = json.load( f, encoding = 'utf-8' )
		table = []
		for firstTopic, vector in enumerate(topicCooccurrence):
			table += [ { 'firstTopic' : firstTopic, 'secondTopic' : secondTopic, 'value' : value } for secondTopic, value in enumerate(vector) ]
		table.sort( key = lambda x : -x['value'] )

		# Responses
		results = {
			'TopicCooccurrence' : table
		}
		self.content.update(results)
		return results

	def LoadTopicCovariance( self ):
		# Load from disk
		self.LoadTopicCooccurrence()
		topicCooccurrence = self.content['TopicCooccurrence']
		normalization = sum( d['value'] for d in topicCooccurrence )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		table = [ { 'firstTopic' : d['firstTopic'], 'secondTopic' : d['secondTopic'], 'value' : d['value'] * normalization } for d in topicCooccurrence ]
		table.sort( key = lambda x : -x['value'] )
		
		# Responses
		results = {
			'TopicCovariance' : table
		}
		self.content.update(results)
		return results

	def LoadTopTerms( self ):
		def GetTopTerms( vector, index ):
			allTerms = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subTerms = allTerms[termOffset:termOffset+termLimit]
			return [ { 'term' : term, 'topic' : index, 'value' : vector[term] } for term in subTerms ]
			
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		topicIndex = self.GetParam('topicIndex')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		table = []
		if topicIndex is None:
			for index, vector in enumerate(matrix):
				table += GetTopTerms( vector, index )
		elif topicIndex < len(matrix):
			table += GetTopTerms( matrix[topicIndex], topicIndex )
		table.sort( key = lambda x : -x['value'] )

		# Responses
		results = {
			'TopTerms' : table
		}
		self.content.update(results)
		return results

	def LoadTopDocs( self ):
		def GetTopDocs( vector, index ):
			allDocs = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subDocs = allDocs[docOffset:docOffset+docLimit]
			return [ { 'docID' : docID, 'topic' : index, 'value' : vector[docID] } for docID in subDocs ]
		
		# Parameters
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		topicIndex = self.GetParam('topicIndex')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-doc-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		table = []
		if topicIndex is None:
			for index, vector in enumerate(matrix):
				table += GetTopDocs( vector, index )
		elif topicIndex < len(matrix):
			table += GetTopDocs( matrix[topicIndex], topicIndex )
		table.sort( key = lambda x : -x['value'] )

		# Responses
		results = {
			'TopDocs' : table
		}
		self.content.update(results)
		return results
