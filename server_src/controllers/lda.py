#!/usr/bin/env python

import os
import json

def index():
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attributes' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		]
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return dataStr
	else:
		data[ 'content' ] = dataStr
		return data

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

def GetDocIndex( limit = 100 ):
	filename = os.path.join( request.folder, 'data/lda', 'doc-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	maxCount = len(content)
	content=content[:limit]
	return content, maxCount

def GetTermIndex( limit = 100 ):
	filename = os.path.join( request.folder, 'data/lda', 'term-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	maxCount = len(content)
	content=content[:limit]
	return content, maxCount

def GetTopicIndex( limit = 50 ):
	filename = os.path.join( request.folder, 'data/lda', 'topic-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	maxCount = len(content)
	content=content[:limit]
	return content, maxCount

def GetTermTopicMatrix( termLimit = 100, topicLimit = 50 ):
	filename = os.path.join( request.folder, 'data/lda', 'term-topic-matrix.txt' )
	content = []
	with open( filename ) as f:
		for line in f:
			values = [ float(value) for value in line[:-1].split('\t') ]
			content.append( values[:topicLimit] )
			if len(content) >= termLimit:
				break
	return content

def GetDocTopicMatrix( docLimit = 100, topicLimit = 50 ):
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
	docLimit = 100
	docIndex, docMaxCount = GetDocIndex( limit = docLimit )
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attribute' : GetModelAttribute(),
		'model_attributes' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		],
		'docLimit' : docLimit,
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'DocIndex' : docIndex
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return dataStr
	else:
		response.view = 'lda/api.html'
		data[ 'content' ] = dataStr
		return data

def TermIndex():
	termLimit = 100
	termIndex, termMaxCount = GetTermIndex( limit = termLimit )
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attribute' : GetModelAttribute(),
		'model_attributes' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		],
		'termLimit' : termLimit,
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'TermIndex' : termIndex
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return dataStr
	else:
		response.view = 'lda/api.html'
		data[ 'content' ] = dataStr
		return data

def TopicIndex():
	topicLimit = 50
	topicIndex, topicMaxCount = GetTopicIndex( limit = topicLimit )
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attribute' : GetModelAttribute(),
		'model_attributes' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		],
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TopicIndex' : topicIndex
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return data
	else:
		response.view = 'lda/api.html'
		data[ 'content' ] = dataStr
		return data

def TermTopicMatrix():
	termLimit = 100
	topicLimit = 50
	termIndex, termMaxCount = GetTermIndex( limit = termLimit )
	topicIndex, topicMaxCount = GetTopicIndex( limit = topicLimit )
	termTopicMatrix = GetTermTopicMatrix( termLimit = termLimit, topicLimit = topicLimit )
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attribute' : GetModelAttribute(),
		'model_attributes' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		],
		'termLimit' : termLimit,
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return dataStr
	else:
		response.view = 'lda/api.html'
		data[ 'content' ] = dataStr
		return data

def DocTopicMatrix():
	docLimit = 100
	topicLimit = 50
	docIndex, docMaxCount = GetDocIndex( limit = docLimit )
	topicIndex, topicMaxCount = GetTopicIndex( limit = topicLimit )
	docTopicMatrix = GetDocTopicMatrix( docLimit = docLimit, topicLimit = topicLimit )
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attribute' : GetModelAttribute(),
		'model_attributes' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		],
		'docLimit' : docLimit,
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'DocIndex' : docIndex,
		'TopicIndex' : topicIndex,
		'DocTopicMatrix' : docTopicMatrix
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	if IsJsonFormat():
		return dataStr
	else:
		response.view = 'lda/api.html'
		data[ 'content' ] = dataStr
		return data
