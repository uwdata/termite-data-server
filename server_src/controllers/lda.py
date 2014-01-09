#!/usr/bin/env python

import os
import json

def test():
	return { 'message' : "Yo" }
	
def index():
	if IsJsonFormat():
		return GenerateJsonResponse()
	else:
		return GenerateHtmlResponse()

def GenerateJsonResponse():
	identifier = {
		'model_type' : 'lda',
		'model_version' : '0.1',
		'model_api' : [
			'DocIndex',
			'TermIndex',
			'TopicIndex',
			'TermTopicMatrix',
			'DocTopicMatrix'
		]
	}
	return json.dumps( identifier, encoding = 'utf-8', indent = 2, sort_keys = True )

def GenerateHtmlResponse():
	text = "This is an LDA model."
	return text
	
	# return { 'message' : 'This is an LDA model generated from an HTML template' }

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
		'api_type' : 'TermIndex',
		'api_version' : '0.1',
		'docLimit' : docLimit,
		'docCount' : len(docIndex),
		'DocIndex' : docIndex
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def TermIndex():
	termLimit = 100
	termIndex = GetTermIndex( limit = termLimit )
	data = {
		'api_type' : 'TermIndex',
		'api_version' : '0.1',
		'termLimit' : termLimit,
		'termCount' : len(termIndex),
		'TermIndex' : termIndex
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def TopicIndex():
	topicLimit = 50
	topicIndex = GetTopicIndex( limit = topicLimit )
	data = {
		'api_type' : 'TopicIndex',
		'api_version' : '0.1',
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
		'TopicIndex' : topicIndex
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def TermTopicMatrix():
	termLimit = 100
	topicLimit = 50
	termIndex = GetTermIndex( limit = termLimit )
	topicIndex = GetTopicIndex( limit = topicLimit )
	termTopicMatrix = GetTermTopicMatrix( termLimit = termLimit, topicLimit = topicLimit )
	data = {
		'api_type' : 'TermTopicMatrix',
		'api_version' : '0.1',
		'termLimit' : termLimit,
		'termCount' : len(termIndex),
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def DocTopicMatrix():
	docLimit = 100
	topicLimit = 50
	docIndex = GetDocIndex( limit = docLimit )
	topicIndex = GetTopicIndex( limit = topicLimit )
	docTopicMatrix = GetDocTopicMatrix( docLimit = docLimit, topicLimit = topicLimit )
	data = {
		'api_type' : 'DocTopicMatrix',
		'api_version' : '0.1',
		'docLimit' : docLimit,
		'docCount' : len(docIndex),
		'topicLimit' : topicLimit,
		'topicCount' : len(topicIndex),
		'DocIndex' : docIndex,
		'TopicIndex' : topicIndex,
		'DocTopicMatrix' : docTopicMatrix
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )
