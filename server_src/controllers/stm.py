#!/usr/bin/env python

import os
import json

def index():
	data = {
		'server_identifier' : GetServerIdentifier(),
		'dataset_identifier' : GetDatasetIdentifier(),
		'model_type' : GetModelType(),
		'model_attributes' : []
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
