#!/usr/bin/env python

import os
import json

def index():
	return GenerateResponse()

def GenerateResponse( keysAndValues = {} ):
	def IsJsonFormat():
		return 'format' in request.vars and 'json' == request.vars['format'].lower()

	def GetServerIdentifier():
		return request.env['HTTP_HOST']

	def GetDatasetIdentifier():
		return request.application

	def GetModelType():
		return request.controller

	def GetModelAttribute():
		return request.function

	def GetModelAttributes():
		return [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		]

	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attribute' : GetModelAttribute(),
		'model_attributes' : GetModelAttributes()
	}
	data.update( keysAndValues )
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return dataStr
	else:
		data[ 'content' ] = dataStr
		return data
	
def GetParams():
	def GetDocLimit():
	    limit = 100
	    if 'docLimit' in request.vars:
			try:
				n = int( request.vars['docLimit'] )
				if n > 0:
					limit = n
			except ValueError:
				pass
	    return limit

	def GetTermLimit():
	    limit = 100
	    if 'termLimit' in request.vars and int( request.vars['termLimit'] ) > 0:
	        limit = int(request.vars['termLimit'])
	    return limit

	def GetTopicLimit():
	    limit = 50
	    if 'topicLimit' in request.vars and int( request.vars['topicLimit'] ) > 0:
	        limit = int(request.vars['topicLimit'])
	    return limit

	params = {
		'docLimit' : GetDocLimit(),
		'termLimit' : GetTermLimit(),
		'topicLimit' : GetTopicLimit()
	}
	return params

def GetDocIndex( params ):
	docLimit = params['docLimit']
	filename = os.path.join( request.folder, 'data/lda', 'doc-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	maxCount = len(content)
	content = content[:docLimit]
	return content, maxCount

def GetTermIndex( params ):
	termLimit = params['termLimit']
	filename = os.path.join( request.folder, 'data/lda', 'term-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	maxCount = len(content)
	content = content[:termLimit]
	return content, maxCount

def GetTopicIndex( params ):
	topicLimit = params['topicLimit']
	filename = os.path.join( request.folder, 'data/lda', 'topic-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	maxCount = len(content)
	content = content[:topicLimit]
	return content, maxCount

def GetTermTopicMatrix( params ):
	termLimit = params['termLimit']
	topicLimit = params['topicLimit']
	filename = os.path.join( request.folder, 'data/lda', 'term-topic-matrix.txt' )
	content = []
	with open( filename ) as f:
		for line in f:
			values = [ float(value) for value in line[:-1].split('\t') ]
			content.append( values[:topicLimit] )
			if len(content) >= termLimit:
				break
	return content

def GetDocTopicMatrix( params ):
	docLimit = params['docLimit']
	topicLimit = params['topicLimit']
	filename = os.path.join( request.folder, 'data/lda', 'doc-topic-matrix.txt' )
	content = []
	with open( filename ) as f:
		for line in f:
			values = [ float(value) for value in line[:-1].split('\t') ]
			content.append( values[:topicLimit] )
			if len(content) >= docLimit:
				break
	return content

def DocIndex():
	params = GetParams()
	docIndex, docMaxCount = GetDocIndex( params )
	return GenerateResponse({
		'params' : params,
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'DocIndex' : docIndex
	})

def TermIndex():
	params = GetParams()
	termIndex, termMaxCount = GetTermIndex( params )
	return GenerateResponse({
		'params' : params,
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'TermIndex' : termIndex
	})

def TopicIndex():
	params = GetParams()
	topicIndex, topicMaxCount = GetTopicIndex( params )
	return GenerateResponse({
		'params' : params,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TopicIndex' : topicIndex
	})

def TermTopicMatrix():
	params = GetParams()
	termIndex, termMaxCount = GetTermIndex( params )
	topicIndex, topicMaxCount = GetTopicIndex( params )
	termTopicMatrix = GetTermTopicMatrix( params )
	return GenerateResponse({
		'params' : params,
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix
	})

def DocTopicMatrix():
	params = GetParams()
	docIndex, docMaxCount = GetDocIndex( params )
	topicIndex, topicMaxCount = GetTopicIndex( params )
	docTopicMatrix = GetDocTopicMatrix( params )
	return GenerateResponse({
		'params' : params,
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'DocIndex' : docIndex,
		'TopicIndex' : topicIndex,
		'DocTopicMatrix' : docTopicMatrix
	})
