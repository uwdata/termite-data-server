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
	return {}
	
def DocMeta():
	params = GetParams()
	return GenerateResponse({
		'params' : params
	})
