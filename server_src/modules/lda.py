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
		
		# Processing
		subTerms = allTerms[termOffset:termOffset+termLimit]
		table = [ { 'index' : index, 'text' : term['text'] } for index, term in enumerate(subTerms) ]
		header = [
			{ 'name' : 'index', 'type' : 'number' },
			{ 'name' : 'text', 'type' : 'string' } 
		]
		termMaxCount = len(allTerms)
		termCount = len(subTerms)
		
		# Responses
		self.content.update({
			'TermIndex' : table,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount
		})
		self.table = table
		self.header = header

	def LoadDocIndex( self ):
		# Parameters
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-index.json' )
		with open( filename ) as f:
			allDocs = json.load( f, encoding = 'utf-8' )

		# Processing
		subDocs = allDocs[docOffset:docOffset+docLimit]
		table = [ { 'index' : index, 'docID' : doc['docID'] } for index, doc in enumerate(subDocs) ]
		header = [
			{ 'name' : 'index', 'type' : 'number' },
			{ 'name' : 'docID', 'type' : 'string' }
		]
		docMaxCount = len(allDocs)
		docCount = len(subDocs)

		# Responses
		self.content.update({
			'DocIndex' : table,
			'DocCount' : docCount,
			'DocMaxCount' : docMaxCount
		})
		self.table = table
		self.header = header

	def LoadTopicIndex( self ):
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-index.json' )
		with open( filename ) as f:
			allTopics = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = [ { 'index' : index, 'name' : 'Topic #{}'.format(topic['index']+1) } for index, topic in enumerate(allTopics) ]
		header = [
			{ 'name' : 'index', 'type' : 'number' },
			{ 'name' : 'name', 'type' : 'string' }
		]
		topicCount = len(allTopics)

		# Responses
		self.content.update({
			'TopicIndex' : table,
			'TopicCount' : topicCount,
			'TopicMaxCount' : topicCount
		})
		self.table = table
		self.header = header
	
	def LoadTermTopicMatrix( self ):
		# Parameters
		self.LoadTermIndex()
		self.LoadTopicIndex()
		termSet = frozenset( d['text'] for d in self.content['TermIndex'] )
		threshold = self.GetParam('threshold')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'term-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		for term in termSet:
			table += [ { 'term' : term, 'topic' : index, 'value' : value } for index, value in enumerate(matrix[term]) if value > threshold ]
		table.sort( key = lambda x : -x['value'] )
		header = [
			{ 'name' : 'term', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TermTopicMatrix' : table
		})
		self.table = table
		self.header = header

	def LoadTopicTermMatrix( self ):
		# Parameters
		self.LoadTermIndex()
		self.LoadTopicIndex()
		termSet = frozenset( d['text'] for d in self.content['TermIndex'] )
		threshold = self.GetParam('threshold')

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		for index, vector in enumerate(matrix):
			table += [ { 'term' : term, 'topic' : index, 'value' : vector[term] } for term in termSet if term in vector ]
		table.sort( key = lambda x : -x['value'] )
		header = [
			{ 'name' : 'term', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]

		self.content.update({
			'TopicTermMatrix' : table
		})
		self.table = table
		self.header = header
	
	def LoadDocTopicMatrix( self ):
		# Parameters
		self.LoadDocIndex()
		self.LoadTopicIndex()
		docSet = frozenset( d['docID'] for d in self.content['DocIndex'] )
		threshold = self.GetParam('threshold')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		for docID in docSet:
			table += [ { 'docID' : docID, 'topic' : index, 'value' : value } for index, value in enumerate(matrix[docID]) if value > threshold ]
		table.sort( key = lambda x : -x['value'] )
		header = [
			{ 'name' : 'docID', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]
		
		# Responses
		self.content.update({
			'DocTopicMatrix' : table
		})
		self.table = table
		self.header = header
	
	def LoadTopicDocMatrix( self ):
		# Parameters
		self.LoadDocIndex()
		self.LoadTopicIndex()
		docSet = frozenset( d['docID'] for d in self.content['DocIndex'] )
		threshold = self.GetParam('threshold')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-doc-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		for index, vector in enumerate(matrix):
			table += [ { 'docID' : docID, 'topic' : index, 'value' : vector[docID] } for docID in docSet if docID in vector ]
		table.sort( key = lambda x : -x['value'] )
		header = [
			{ 'name' : 'docID', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TopicDocMatrix' : table
		})
		self.table = table
		self.header = header
		
	def LoadTopicCooccurrence( self ):
		# Load from disk
		self.LoadTopicIndex()
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-cooccurrence.json' )
		with open( filename ) as f:
			topicCooccurrence = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		for firstTopic, vector in enumerate(topicCooccurrence):
			table += [ { 'firstTopic' : firstTopic, 'secondTopic' : secondTopic, 'value' : value } for secondTopic, value in enumerate(vector) ]
		table.sort( key = lambda x : -x['value'] )
		header = [
			{ 'name' : 'firstTopic', 'type' : 'number' },
			{ 'name' : 'secondTopic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TopicCooccurrence' : table
		})
		self.table = table
		self.header = header

	def LoadTopicCovariance( self ):
		# Load from disk
		self.LoadTopicIndex()
		self.LoadTopicCooccurrence()
		
		# Processing
		topicCooccurrence = self.content['TopicCooccurrence']
		normalization = sum( d['value'] for d in topicCooccurrence )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		table = [ { 'firstTopic' : d['firstTopic'], 'secondTopic' : d['secondTopic'], 'value' : d['value'] * normalization } for d in topicCooccurrence ]
		table.sort( key = lambda x : -x['value'] )
		header = [
			{ 'name' : 'firstTopic', 'type' : 'number' },
			{ 'name' : 'secondTopic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]
		
		# Responses
		self.content.update({
			'TopicCovariance' : table
		})
		self.table = table
		self.header = header

	def LoadTopTerms( self ):
		def GetTopTerms( vector, index ):
			allTerms = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subTerms = allTerms[termOffset:termOffset+termLimit]
			for term in subTerms:
				if term not in vocabSet:
					vocabSet.add(term)
					vocabList.append(term)
			return [ { 'term' : term, 'topic' : index, 'value' : vector[term] } for term in subTerms ]
			
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		tIndex = self.GetParam('topicIndex')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		vocabList = []
		vocabSet = set()
		topicIndex = []
		if tIndex is None:
			for index, vector in enumerate(matrix):
				table += GetTopTerms( vector, index )
				topicIndex.append( { 'index' : index, 'name' : 'Topic #{}'.format(index+1) } )
		else:
			if tIndex < len(matrix):
				table += GetTopTerms( matrix[tIndex], tIndex )
				topicIndex.append( { 'index' : tIndex, 'name' : 'Topic #{}'.format(tIndex+1) } )
		table.sort( key = lambda x : -x['value'] )
		topicCount = len(topicIndex)
		topicMaxCount = len(matrix)
		termIndex = [ { 'index' : n, 'text' : term } for n, term in enumerate(vocabList) ]
		termCount = len(termIndex)
		header = [
			{ 'name' : 'term', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TopTerms' : table,
			'TopicIndex' : topicIndex,
			'TermIndex' : termIndex,
			'TopicCount' : topicCount,
			'TopicMaxCount' : topicMaxCount,
			'TermCount' : termCount
		})
		self.table = table
		self.header = header

	def LoadTopDocs( self ):
		def GetTopDocs( vector, index ):
			allDocs = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subDocs = allDocs[docOffset:docOffset+docLimit]
			for docID in subDocs:
				if docID not in docSet:
					docSet.add(docID)
					docList.append(docID)
			return [ { 'docID' : docID, 'topic' : index, 'value' : vector[docID] } for docID in subDocs ]
		
		# Parameters
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		tIndex = self.GetParam('topicIndex')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-doc-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		
		# Processing
		table = []
		docList = []
		docSet = set()
		topicIndex = []
		if tIndex is None:
			for index, vector in enumerate(matrix):
				table += GetTopDocs( vector, index )
				topicIndex.append( { 'index' : index, 'name' : 'Topic #{}'.format(index+1) } )
		else:
			if tIndex < len(matrix):
				table += GetTopDocs( matrix[tIndex], tIndex )
				topicIndex.append( { 'index' : tIndex, 'name' : 'Topic #{}'.format(tIndex+1) } )
		table.sort( key = lambda x : -x['value'] )
		topicCount = len(topicIndex)
		topicMaxCount = len(matrix)
		docIndex = [ { 'index' : n, 'docID' : docID } for n, docID in enumerate(docList) ]
		docCount = len(docIndex)
		header = [
			{ 'name' : 'docID', 'type' : 'string' },
			{ 'name' : 'topic', 'type' : 'number' },
			{ 'name' : 'value', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TopDocs' : table,
			'TopicIndex' : topicIndex,
			'DocIndex' : docIndex,
			'TopicCount' : topicCount,
			'TopicMaxCount' : topicMaxCount,
			'DocCount' : docCount
		})
		self.table = table
		self.header = header
