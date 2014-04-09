#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import random
import subprocess
from datetime import datetime

FORBIDDEN_APP_NAMES = frozenset( [ 'init', 'welcome', 'admin' ] )
EMPTY_SUBFOLDERS = [ 'data', 'databases' ]
LINKED_SUBFOLDERS = [ 'models', 'views', 'controllers', 'static', 'modules' ]

class CreateApp( object ):
	
	def __init__( self, app_name, APPS_ROOT = 'apps', SERVER_RELATIVE_PATH = '../../server_src' ):
		self.APPS_ROOT = APPS_ROOT
		self.SERVER_RELATIVE_PATH = SERVER_RELATIVE_PATH
		self.logger = logging.getLogger('termite')
		
		if app_name in FORBIDDEN_APP_NAMES:
			self.app_name = '{}-{}'.format( app_name, self.GetTimestamp() )
			self.logger.warning( 'Disallowed application name: %s -> %s', app_name, self.app_name )
		else:
			self.app_name = app_name
		self.app_temporary_path = '{}/{}'.format( self.APPS_ROOT, self.GetRandomIdentifier() )
		self.app_final_path = '{}/{}'.format( self.APPS_ROOT, self.app_name )

	def RunCommand( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )

	def GetRandomIdentifier( self ):
		return '-'.join( '{:04d}'.format(random.randint(0,9999)) for i in range(6) )
		
	def GetTimestamp( self ):
		return datetime.now().strftime("%Y%m%d-%H%M%S-%f")
	
	def GetPath( self ):
		return self.app_temporary_path

	def __enter__( self ):
		self.logger.info( 'Creating application: %s (%s)', self.app_name, self.app_temporary_path )
		os.makedirs( self.app_temporary_path )
	
		for subfolder in EMPTY_SUBFOLDERS:
			pathname = '{}/{}'.format( self.app_temporary_path, subfolder )
			if not os.path.exists( pathname ):
				self.logger.info( 'Creating folder: %s', pathname )
				os.makedirs( pathname )
	
		for subfolder in LINKED_SUBFOLDERS:
			pathname = '{}/{}'.format( self.app_temporary_path, subfolder )
			if not os.path.exists( pathname ):
				self.logger.info( 'Linking folder: %s', pathname )
				self.RunCommand( [ 'ln', '-s', '{}/{}'.format(self.SERVER_RELATIVE_PATH, subfolder), pathname ] )
	
		filename = '{}/__init__.py'.format(self.app_temporary_path)
		if not os.path.exists( filename ):
			self.logger.info( 'Creating file: %s', filename )
			self.RunCommand( [ 'touch', filename ] )
		
		return self
	
	def __exit__( self, type, value, traceback ):
		if os.path.exists( self.app_final_path ):
			app_backup_path = '{}/{}-{}'.format( self.APPS_ROOT, self.app_name, self.GetTimestamp() )
			self.logger.info( 'Backing up existing application: %s [%s] -> [%s]', self.app_name, self.app_final_path, app_backup_path )
			self.RunCommand( [ 'mv', self.app_final_path, app_backup_path ] )
		
		if type is None:
			self.logger.info( 'Moving application into place: %s [%s] -> [%s]', self.app_name, self.app_temporary_path, self.app_final_path )
			self.RunCommand( [ 'mv', self.app_temporary_path, self.app_final_path ] )
		else:
			self.logger.warning( 'An error occured while creating application: %s [%s]', self.app_name, self.app_temporary_path )
			