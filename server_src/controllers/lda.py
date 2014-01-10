#!/usr/bin/env python

import os
import json

def index():
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_type' : 'lda',
		'model_api' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		]
	}
	if IsJsonFormat():
		return json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	else:
		return data

def IsJsonFormat():
	return 'format' in request.vars and 'json' == request.vars['format'].lower()

def GetDocIndex( limit = 100 ):
	filename = os.path.join( request.folder, 'data/lda', 'doc-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	return content[:limit]

def GetTermIndex( limit = 100 ):
	filename = os.path.join( request.folder, 'data/lda', 'term-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	return content[:limit]

def GetTopicIndex( limit = 50 ):
	filename = os.path.join( request.folder, 'data/lda', 'topic-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	return content[:limit]

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
	docIndex = GetDocIndex( limit = docLimit )
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_type' : 'lda',
		'api_type' : 'TermIndex',
		'docLimit' : docLimit,
		'docCount' : len(docIndex),
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
	termIndex = GetTermIndex( limit = termLimit )
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_type' : 'lda',
		'api_type' : 'TermIndex',
		'termLimit' : termLimit,
		'termCount' : len(termIndex),
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
	topicIndex = GetTopicIndex( limit = topicLimit )
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_type' : 'lda',
		'api_type' : 'TermIndex',
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
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
	termIndex = GetTermIndex( limit = termLimit )
	topicIndex = GetTopicIndex( limit = topicLimit )
	termTopicMatrix = GetTermTopicMatrix( termLimit = termLimit, topicLimit = topicLimit )
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_type' : 'lda',
		'api_type' : 'TermIndex',
		'termLimit' : termLimit,
		'termCount' : len(termIndex),
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
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
	docIndex = GetDocIndex( limit = docLimit )
	topicIndex = GetTopicIndex( limit = topicLimit )
	docTopicMatrix = GetDocTopicMatrix( docLimit = docLimit, topicLimit = topicLimit )
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_type' : 'lda',
		'api_type' : 'TermIndex',
		'docLimit' : docLimit,
		'docCount' : len(docIndex),
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
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
