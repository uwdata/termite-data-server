#!/usr/bin/env python

import os
import json

class TermiteCore( object ):
	def __init__( self, request, response ):
		self.request = request
		self.response = response
		self.configs = self.GetConfigs()
		self.params = {}
		self.content = {}

################################################################################		
# Server, Dataset, Model, and Attribute

	EXCLUDED_FOLDERS = frozenset( [ 'admin', 'examples', 'welcome', 'init' ] )

	def GetServer( self ):
		return self.request.env['HTTP_HOST']

	def GetDataset( self ):
		return self.request.application

	def GetModel( self ):
		return self.request.controller

	def GetAttribute( self ):
		return self.request.function

	def GetDatasets( self ):
		folders = []
		applications_path = '{}/applications'.format( self.request.env['applications_parent'] )
		for folder in os.listdir( applications_path ):
			if folder not in TermiteCore.EXCLUDED_FOLDERS:
				applications_subpath = '{}/{}'.format( applications_path, folder )
				if os.path.isdir( applications_subpath ):
					folders.append( folder )
		folders = sorted( folders )
		return folders
	
	def GetModels( self, dataset ):
		if dataset in TermiteCore.EXCLUDED_FOLDERS:
			return None
		folders = [ 'vis' ]
		app_data_path = '{}/data'.format( self.request.folder )
		for folder in os.listdir( app_data_path ):
			app_data_subpath = '{}/{}'.format( app_data_path, folder )
			if os.path.isdir( app_data_subpath ):
				folders.append( folder )
		folders = sorted( folders )
		return folders
	
	def GetAttributes( self, dataset, model ):
		if dataset in TermiteCore.EXCLUDED_FOLDERS:
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
				'TopicTermMatrix',
				'TopicDocMatrix',
				'TopicCooccurrence',
				'TopicCovariance',
				'TopicTopTerms',
				'TopicTopDocs'
			]
		if model == 'corpus':
			return [
				'Document',
				'TextSearch',
				'TermFreqs',
				'TermCoFreqs',
				'TermProbs',
				'TermCoProbs',
				'TermPMI'
			]
		if model == 'vis':
			return [
				'GroupInABox',
				'CovariateChart'
			]
		return []
	
	def GetConfigs( self ):
		server = self.GetServer()
		dataset = self.GetDataset()
		datasets = self.GetDatasets()
		model = self.GetModel()
		models = self.GetModels( dataset )
		attribute = self.GetAttribute()
		attributes = self.GetAttributes( dataset, model )
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
	
################################################################################
# Parameters
	def GetStringParam( self, key ):
		if key in self.request.vars:
			return unicode( self.request.vars[key] )
		else:
			return u''
		
	def GetNonNegativeIntegerParam( self, key, defaultValue ):
		try:
			n = int( self.request.vars[ key ] )
			if n >= 0:
				return n
			else:
				return 0
		except:
			return defaultValue
	
################################################################################
# Generate a response

	def IsDebugMode( self ):
		return 'debug' in self.request.vars
	
	def IsJsonFormat( self ):
		return 'format' in self.request.vars and 'json' == self.request.vars['format'].lower()
	
	def HasAllowedOrigin( self ):
		return 'origin' in self.request.vars
	
	def GetAllowedOrigin( self ):
		return self.request.vars['origin']
	
	def GenerateResponse( self ):
		if self.IsDebugMode():
			return self.GenerateDebugResponse()
		else:
			return self.GenerateNormalResponse()
	
	def GenerateDebugResponse( self ):
		envObject = self.request.env
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
				envJSON[ key ] = 'value not JSON-serializable'
		
		data = {
			'env' : envJSON,
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
			'now' : str( self.request.now ),
			'configs' : self.configs,
			'params' : self.params
		}
		data.update( self.content )
		dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		self.response.headers['Content-Type'] = 'application/json'
		return dataStr

	def GenerateNormalResponse( self ):
		data = {
			'configs' : self.configs,
			'params' : self.params
		}
		data.update( self.content )
		dataStr = json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		if self.IsJsonFormat():
			self.response.headers['Content-Type'] = 'application/json'
			if self.HasAllowedOrigin():
				self.response.headers['Access-Control-Allow-Origin'] = self.GetAllowedOrigin()
			return dataStr
		else:
			self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
			data[ 'content' ] = dataStr
			return data
