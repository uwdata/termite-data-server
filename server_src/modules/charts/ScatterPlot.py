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
		
		if key == 'firstDim':
			value = self.GetStringParam( key )
			self.params.update({ key : value })
		
		if key == 'secondDim':
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
	
	def PrepareChart( self ):
		# Parameters
		self.LoadTopicIndex()
		self.LoadDocIndex()
		topicIndex = self.content['TopicIndex']
		docLimit = self.GetParam('docLimit')
		docOffset = self.GetParam('docOffset')
		firstDim = self.GetParam('firstDim')
		secondDim = self.GetParam('secondDim')
		
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
		dimensions = corpusHeader
		dimensions += [ { 'name' : d['name'], 'index' : d['index'], 'type' : 'number' } for d in topicIndex ]
		header = [
			{ 'name' : 'DocID', 'type' : 'string' }
		]
		for dimension in dimensions:
			if dimension['name'] == firstDim:
				header.append(dimension)
		for dimension in dimensions:
			if dimension['name'] == secondDim:
				header.append(dimension)
		fullTable = corpusData.values()
		subTable = fullTable[docOffset:docOffset+docLimit]
		table = []
		for record in subTable:
			docID = record['DocID']
			row = { 'DocID' : docID }
			for key in record.iterkeys():
				if key == firstDim or key == secondDim:
					row[key] = record[key]
			for d in topicIndex:
				if d['name'] == firstDim or d['name'] == secondDim:
					row[d['name']] = matrix[docID][d['index']]
			table.append(row)
		docCount = len(table)
		docMaxCount = len(fullTable)
		
		self.content.update({
			'Dimensions' : dimensions,
			'Header' : header,
			'Data' : table
		})
		self.table = table
		self.header = header
