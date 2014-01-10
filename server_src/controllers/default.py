#!/usr/bin/env python

import os
import json

def index():
	if IsDebugFormat():
		return GenerateDebugResponse()
	else:
		return GenerateNormalResponse()

def IsJsonFormat():
	return 'format' in request.vars and 'json' == request.vars['format'].lower()

def IsDebugFormat():
	return 'format' in request.vars and 'debug' == request.vars['format'].lower()

def GenerateDebugResponse():
	def GetEnv( env ):
		data = {}
		for key in env:
			value = env[key]
			if isinstance( value, dict ) or \
			   isinstance( value, list ) or isinstance( value, tuple ) or \
			   isinstance( value, str ) or isinstance( value, unicode ) or \
			   isinstance( value, int ) or isinstance( value, long ) or isinstance( value, float ) or \
			   value is None or value is True or value is False:
				data[ key ] = value
			else:
				data[ key ] = 'N/A'
		return data
	
	info = {
		'env' : GetEnv( request.env ),
		'cookies' : request.cookies,
		'vars' : request.vars,
		'get_vars' : request.get_vars,
		'post_vars' : request.post_vars,
		'folder' : request.folder,
		'application' : request.application,
		'function' : request.function,
		'args' : request.args,
		'extension' : request.extension,
		'now' : str( request.now )
	}
	return json.dumps( info, encoding = 'utf-8', indent = 2, sort_keys = True )

def GenerateNormalResponse():
	data = {
		'server_type' : 'topic_models',
		'dataset_identifier' : '20newsgroups',
		'model_types' : [
			'lda'
		]
	}
	if IsJsonFormat():
		return json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	else:
		body = {
			'server_type' : "<a href='/'>topic_models</a>",
			'dataset_identifier' : "<b>20newsgroups</b>",
			'model_types' : [
				"<a href='lda/'>lda</a>"
			]
		}
		data[ "body" ] = json.dumps( body, encoding = 'utf-8', indent = 2, sort_keys = True )
		return data
