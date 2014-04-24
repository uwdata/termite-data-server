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
RELATIVE_SERVER_SRC = '../../server_src'

class CreateApp( object ):
	
	def __init__( self, appName, APPS_ROOT = 'apps' ):
		self.logger = logging.getLogger('termite')
		self.APPS_ROOT = APPS_ROOT
		
		if appName in FORBIDDEN_APP_NAMES:
			self.appName = '{}_{}'.format( appName, self.GetTimestamp() )
			self.logger.warning( 'Disallowed application name: %s --> %s', appName, self.appName )
		else:
			self.appName = appName
		self.appTempPath = '{}/temp_{}'.format( self.APPS_ROOT, self.GetTimestamp() )
		self.appFinalPath = '{}/{}'.format( self.APPS_ROOT, self.appName )
	
	def RunCommand( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )
	
	def GetTimestamp( self ):
		formatter = '%Y%m%d_%H%M%S_%f_{:04d}'.format(random.randint(0,9999))
		return datetime.now().strftime(formatter)
	
	def GetPath( self ):
		return self.appTempPath
	
	def GetDataPath( self ):
		return '{}/data'.format( self.appTempPath )
	
	def GetDatabasePath( self ):
		return '{}/databases'.format( self.appTempPath )
	
	def __enter__( self ):
		self.logger.info( 'Creating app: %s [%s]', self.appName, self.appTempPath )
		if not os.path.exists( self.appTempPath ):
			os.makedirs( self.appTempPath )
		
		for subfolder in EMPTY_SUBFOLDERS:
			pathname = '{}/{}'.format( self.appTempPath, subfolder )
			if not os.path.exists( pathname ):
				self.logger.info( 'Creating folder: [%s]', pathname )
				os.makedirs( pathname )
		
		for subfolder in LINKED_SUBFOLDERS:
			pathname = '{}/{}'.format( self.appTempPath, subfolder )
			if not os.path.exists( pathname ):
				self.logger.info( 'Linking folder: [%s]', pathname )
				os.symlink( '{}/{}'.format(RELATIVE_SERVER_SRC, subfolder), pathname )
		
		filename = '{}/__init__.py'.format(self.appTempPath)
		if not os.path.exists( filename ):
			self.logger.info( 'Creating file: [%s]', filename )
			with open( filename, 'w' ) as f:
				pass
		
		return self
	
	def __exit__( self, type, value, traceback ):
		if type is None:
			if os.path.exists( self.appFinalPath ):
				app_backup_path = '{}/{}-{}'.format( self.APPS_ROOT, self.appName, self.GetTimestamp() )
				self.logger.info( 'Backing up existing app: %s [%s] -> [%s]', self.appName, self.appFinalPath, app_backup_path )
				self.RunCommand( [ 'mv', self.appFinalPath, app_backup_path ] )
			self.logger.info( 'Moving app into place: %s [%s] -> [%s]', self.appName, self.appTempPath, self.appFinalPath )
			self.RunCommand( [ 'mv', self.appTempPath, self.appFinalPath ] )
		else:
			self.logger.warning( 'An error occured while creating app: %s [%s]', self.appName, self.appFinalPath )
