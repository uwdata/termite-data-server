#!/usr/bin/env python

import os
import json

def index():
	if IsDebugFormat():
		return GenerateDebugResponse()
	elif IsJsonFormat():
		return GenerateJsonResponse()
	else:
		return GenerateHtmlResponse()

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

def GenerateJsonResponse():
	identifier = {
		'server_type' : 'topic-models',
		'server_version' : '0.1',
		'server_models' : [
			'lda'
		]
	}
	return json.dumps( identifier, encoding = 'utf-8', indent = 2, sort_keys = True )

def GenerateHtmlResponse():
	text = "This is a Termite server."
	return text
