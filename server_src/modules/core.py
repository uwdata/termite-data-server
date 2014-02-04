#!/usr/bin/env python

import os
import json

class TermiteCore:
	def __init__( self, request, response ):
		self.request = request
		self.response = response
	
	def GetConfigs( self ):
		def GetServer():
			return self.request.env['HTTP_HOST']
		
		def GetDataset():
			return self.request.application
		
		def GetModel():
			return self.request.controller
		
		def GetAttribute():
			return self.request.function
		
		def GetDatasets( dataset ):
			FOLDER_EXCLUSIONS = frozenset( [ 'admin', 'examples', 'welcome', 'init' ] )
			applications_parent = self.request.env['applications_parent']
			applications_path = '{}/applications'.format( applications_parent )
			folders = []
			for folder in os.listdir( applications_path ):
				applications_subpath = '{}/{}'.format( applications_path, folder )
				if os.path.isdir( applications_subpath ):
					if folder not in FOLDER_EXCLUSIONS:
						folders.append( folder )
			folders = sorted( folders )
			return folders
		
		def GetModels( dataset, model ):
			if dataset == 'init':
				return None
			
			app_data_path = '{}/data'.format( self.request.folder )
			folders = [ 'vis' ]
			for folder in os.listdir( app_data_path ):
				app_data_subpath = '{}/{}'.format( app_data_path, folder )
				if os.path.isdir( app_data_subpath ):
					folders.append( folder )
			folders = sorted( folders )
			return folders
		
		def GetAttributes( dataset, model, attribute ):
			if dataset == 'init':
				return None
			if model == 'default':
				return None
			
			if model == 'lda':
				return [
					'DocIndex',
					'TermIndex',
					'TopicIndex',
					'TermTopicMatrix',
					'DocTopicMatrix',
					'TopicCooccurrence'
				]
			elif model == 'corpus':
				return [
					'DocMeta',
					'TermFreqs',
					'TermCoFreqs'
				]
			elif model == 'vis':
				return [
					'GroupInABox'
				]
			else:
				return []
		
		server = GetServer()
		dataset = GetDataset()
		datasets = GetDatasets( dataset )
		model = GetModel()
		models = GetModels( dataset, model )
		attribute = GetAttribute()
		attributes = GetAttributes( dataset, model, attribute )
		
		configs = {
			'server' : server,
			'dataset' : dataset,
			'datasets' : datasets,
			'model' : model,
			'models' : models,
			'attribute' : attribute,
			'attributes' : attributes
		}
		return configs
	
	def IsDebugMode( self ):
		return 'debug' in self.request.vars
	
	def IsJsonFormat( self ):
		return 'format' in self.request.vars and 'json' == self.request.vars['format'].lower()
	
	def GenerateResponse( self, params = {}, keysAndValues = {} ):
		if self.IsDebugMode():
			return self.GenerateDebugResponse()
		else:
			return self.GenerateNormalResponse( params, keysAndValues )
	
	def GenerateDebugResponse( self ):
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
			'env' : GetEnv( self.request.env ),
			'cookies' : self.request.cookies,
			'vars' : self.request.vars,
			'get_vars' : self.request.get_vars,
			'post_vars' : self.request.post_vars,
			'folder' : self.request.folder,
			'application' : self.request.application,
			'controller' : self.request.controller,
			'function' : self.request.function,
			'args' : self.request.args,
			'extension' : self.request.extension,
			'now' : str( self.request.now )
		}
		return json.dumps( info, encoding = 'utf-8', indent = 2, sort_keys = True )
	
	
	def GenerateNormalResponse( self, params, keysAndValues = {} ):
		data = {
			'params' : params,
			'configs' : self.GetConfigs()
		}
		data.update( keysAndValues )
		dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		# Workaround while we build up the server-client architecture
		self.response.headers['Access-Control-Allow-Origin'] = 'http://' + self.request.env['REMOTE_ADDR'] + ':8080'
		if self.IsJsonFormat():
			return dataStr
		else:
			data[ 'content' ] = dataStr
			return data
