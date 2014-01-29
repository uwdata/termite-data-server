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
			'DocMeta'
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
	def GetNonNegativeInteger( key, defaultValue ):
		try:
			n = int( request.vars[ key ] )
			if n >= 0:
				return n
			else:
				return 0
		except:
			return defaultValue
	
	def GetString( key, defaultValue ):
		if key in request.vars:
			return request.vars[ key ]
		else:
			return defaultValue

	params = {
		'searchLimit' : GetNonNegativeInteger( 'searchLimit', 100 ),
		'searchOffset' : GetNonNegativeInteger( 'searchOffset', 0 ),
		'searchText' : GetString( 'searchText', '' ),
		'searchOrdering' : GetString( 'searchOrdering', '' )
	}
	return params

def GetDocMeta( params ):
	filename = os.path.join( request.folder, 'data/corpus', 'doc-meta.json' )
	with open( filename ) as f:
		content = json.load( f, encoding = 'utf-8' )
		
		# get params, setup results
		results = {}
		searchText = params["searchText"]
		searchLimit = params["searchLimit"]
		searchOffset = params["searchOffset"]

		matchCount = 0
		keys = sorted(content.keys())
		for index in range(len(keys)):
		    obj = content[keys[index]]
		    docContent = obj["DocContent"]
		    if searchText in docContent:
		        matchCount += 1
		        if matchCount <= searchLimit and index >= searchOffset:
		           results[obj["DocID"]] = obj
	results["metadata"] = {"numResults" : len(results), "totalMatches" : matchCount }
	return results

def DocMeta():
	params = GetParams()
	docs = GetDocMeta( params )
	return GenerateResponse({
		'params' : params,
		'Documents' : docs
	})
