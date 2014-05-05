#!/usr/bin/env python

import json

def index():
	envObject = request.env
	envJSON = {}
	for key in envObject:
		value = envObject[ key ]
		if isinstance( value, dict ) or \
		   isinstance( value, list ) or isinstance( value, tuple ) or \
		   isinstance( value, str ) or isinstance( value, unicode ) or \
		   isinstance( value, int ) or isinstance( value, long ) or isinstance( value, float ) or \
		   value is None or value is True or value is False:
			envJSON[ key ] = value
		else:
			envJSON[ key ] = 'Value not JSON-serializable'

	data = {
		'env' : envJSON,
		'cookies' : request.cookies,
		'vars' : request.vars,
		'get_vars' : request.get_vars,
		'post_vars' : request.post_vars,
		'folder' : request.folder,
		'application' : request.application,
		'controller' : request.controller,
		'function' : request.function,
		'args' : request.args,
		'extension' : request.extension,
		'now' : str( request.now )
	}
	dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
	response.headers['Content-Type'] = 'application/json'
	return dataStr
