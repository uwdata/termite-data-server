#!/usr/bin/env python

import os
import json

def index():
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
	return json.dumps( identifier, encoding = 'utf-8', indent = 2 )

def GerDocIndex():
	filename = os.path.join( request.folder, 'data/lda', 'doc-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	return content

def GetTermIndex():
	filename = os.path.join( request.folder, 'data/lda', 'term-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	return content

def GetTopicIndex():
	filename = os.path.join( request.folder, 'data/lda', 'topic-index.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
	return content

def GetTermTopicMatrix():
	filename = os.path.join( request.folder, 'data/lda', 'term-topic-matrix.txt' )
	with open( filename ) as f:
		content = [ [ float(value) for value in line.split('\t') ] for line in f.read().decode( 'utf-8' ).splitlines() ]
	return content

def GetDocTopicMatrix():
	filename = os.path.join( request.folder, 'data/lda', 'doc-topic-matrix.txt' )
	with open( filename ) as f:
		content = [ [ float(value) for value in line.split('\t') ] for line in f.read().decode( 'utf-8' ).splitlines() ]
	return content

def DocIndex():
	data = {
		'api_type' : 'TermIndex',
		'api_version' : '0.1',
		'DocIndex' : GetDocIndex()
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def TermIndex():
	data = {
		'api_type' : 'TermIndex',
		'api_version' : '0.1',
		'TermIndex' : GetTermIndex()
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def TopicIndex():
	data = {
		'api_type' : 'TopicIndex',
		'api_version' : '0.1',
		'TopicIndex' : GetTopicIndex()
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def TermTopicMatrix():
	data = {
		'api_type' : 'TermTopicMatrix',
		'api_version' : '0.1',
		'TermIndex' : GetTermIndex(),
		'TopicIndex' : GetTopicIndex(),
		'TermTopicMatrix' : GetTermTopicMatrix()
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )

def DocTopicMatrix():
	data = {
		'api_type' : 'DocTopicMatrix',
		'api_version' : '0.1',
		'DocIndex' : GetDocIndex(),
		'TopicIndex' : GetTopicIndex(),
		'TermTopicMatrix' : GetDocTopicMatrix()
	}
	return json.dumps( data, encoding = 'utf-8', sort_keys = True )
