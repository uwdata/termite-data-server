#!/usr/bin/env python

import os
import json
from core import TermiteCore

class ScatterPlot( TermiteCore ):
	def __init__( self, request, response ):
		super( ScatterPlot, self ).__init__( request, response )
	
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
		
		if key == 'xAxis':
			value = self.GetStringParam( key )
			self.params.update({ key : value })
		
		if key == 'yAxis':
			value = self.GetStringParam( key )
			self.params.update({ key : value })
			
		return value

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
			{ 'name' : 'index', 'type' : 'integer' },
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
		table = [ { 'index' : index, 'name' : 'Topic #{}'.format(topic['index']) } for index, topic in enumerate(allTopics) ]
		header = [
			{ 'name' : 'index', 'type' : 'integer' },
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
		
	def LoadTopTerms( self ):
		def GetTopTerms( vector, index ):
			allTerms = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subTerms = allTerms[:5]
			return ', '.join(subTerms)

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )

		# Processing
		topTerms = []
		for index, vector in enumerate(matrix):
			topTerms.append( GetTopTerms( vector, index ) )
		return topTerms
	
	def PrepareChart( self ):
		# Parameters
		self.LoadTopicIndex()
		self.LoadDocIndex()
		topTerms = self.LoadTopTerms()
		topicIndex = self.content['TopicIndex']
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		xAxis = self.GetParam('xAxis')
		yAxis = self.GetParam('yAxis')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/lda', 'doc-topic-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		filename = os.path.join( self.request.folder, 'data/corpus', 'documents-meta.json' )
		with open( filename ) as f:
			corpus = json.load( f, encoding = 'utf-8' )
			corpusHeader = corpus['header']
			corpusData = corpus['data']
			
		# Processing
		xDimensions = [ { 'name' : d['name'], 'label' : d['name'], 'type' : d['type'] } for d in corpusHeader if d['type'] == 'integer' or d['type'] == 'real' ]
		yDimensions = [ { 'name' : d['name'], 'label' : d['name'], 'type' : d['type'] } for d in corpusHeader if d['type'] == 'integer' or d['type'] == 'real' ]
		xDimensions += [ { 'name' : d['name'], 'label' : '{}: {}'.format(d['name'], topTerms[index]), 'index' : d['index'], 'type' : 'real' } for index, d in enumerate(topicIndex) ]
		yDimensions += [ { 'name' : d['name'], 'label' : '{}: {}'.format(d['name'], topTerms[index]), 'index' : d['index'], 'type' : 'real' } for index, d in enumerate(topicIndex) ]
		header = [
			{ 'name' : 'DocID', 'type' : 'string' },
		]
		for d in xDimensions:
			if d['name'] == xAxis:
				header.append( { 'name' : 'x', 'type' : d['type'] } )
		for d in yDimensions:
			if d['name'] == yAxis:
				header.append( { 'name' : 'y', 'type' : d['type'] } )
		fullTable = corpusData.values()
		subTable = fullTable[docOffset:docOffset+docLimit]
		table = []
		for record in subTable:
			docID = record['DocID']
			row = { 'DocID' : docID }
			for key in record.iterkeys():
				if key == xAxis:
					row['x'] = int(record[key])
				if key == yAxis:
					row['y'] = int(record[key])
			for d in topicIndex:
				if d['name'] == xAxis:
					row['x'] = matrix[docID][d['index']]
				if d['name'] == yAxis:
					row['y'] = matrix[docID][d['index']]
			table.append(row)
		docCount = len(table)
		docMaxCount = len(fullTable)
		
		self.content.update({
			'ScatterPlot' : table,
			'Axes' : header,
			'AvailableXDims' : xDimensions,
			'AvailableYDims' : yDimensions
		})
		self.table = table
		self.header = header
