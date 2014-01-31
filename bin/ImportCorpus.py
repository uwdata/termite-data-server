#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import argparse
import logging
import json
import sqlite3

APPS_ROOT = 'apps'
WEB2PY_ROOT = 'tools/web2py'
CORPUS_WRITER = 'utils/mallet/CorpusWriter.jar'
SUBFOLDERS = [ 'models', 'views', 'controllers', 'static', 'modules' ]

class ImportCorpus( object ):
	
	def __init__( self, app_name, app_model = 'corpus', logging_level = 20 ):
		self.app_path = '{}/{}'.format( APPS_ROOT, app_name )
		self.app_data_path = '{}/{}/data/{}'.format( APPS_ROOT, app_name, app_model )
		self.web2py_app_path = '{}/applications/{}'.format( WEB2PY_ROOT, app_name )
		self.logger = logging.getLogger( 'ImportCorpus' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Import corpus information as a web2py application...'                             )
		self.logger.info( '         app = %s', app_name                                                      )
		self.logger.info( '       model = %s', app_model                                                     )
		self.logger.info( '        path = %s', self.app_path                                                 )
		self.logger.info( '      web2py = %s', self.web2py_app_path                                          )
		self.logger.info( '--------------------------------------------------------------------------------' )
		if not os.path.exists( self.app_path ):
			self.logger.info( 'Creating app folder: %s', self.app_path )
			os.makedirs( self.app_path )
		if not os.path.exists( self.app_data_path ):
			self.logger.info( 'Creating app subfolder: %s', self.app_data_path )
			os.makedirs( self.app_data_path )
		for subfolder in SUBFOLDERS:
			app_subpath = '{}/{}'.format( self.app_path, subfolder )
			if not os.path.exists( app_subpath ):
				self.logger.info( 'Linking app subfolder: %s', app_subpath )
				os.system( 'ln -s ../../server_src/{} {}/{}'.format( subfolder, self.app_path, subfolder ) )
		filename = '{}/__init__.py'.format( self.app_path )
		if not os.path.exists( filename ):
			self.logger.info( 'Setting up __init__.py' )
			os.system( 'touch {}'.format( filename ) )
	
	def AddToWeb2py( self ):
		if not os.path.exists( self.web2py_app_path ):
			self.logger.info( 'Adding app to web2py server: %s', self.web2py_app_path )
			os.system( 'ln -s ../../../{} {}'.format( self.app_path, self.web2py_app_path ) )
		self.logger.info( '--------------------------------------------------------------------------------' )
	
	def ImportMeta( self, filename ):
		self.logger.info( 'Importing metadata...' )
		header, meta = self.ExtractDocMeta( filename )
		self.SaveMetaToDisk( meta )
		self.SaveMetaToDB( meta, header )

	def ExtractDocMeta( self, filename ):
		self.logger.info( '    Reading document metadata: %s', filename )
		try:
			with open( filename, 'r' ) as f:
				header = None
				meta = {}
				for index, line in enumerate( f ):
					values = line[:-1].decode( 'utf-8' ).split( '\t' )
					if header is None:
						header = values
					else:
						record = {}
						for n, value in enumerate( values ):
							if n < len(header):
								key = header[n]
							else:
								key = 'Field{:d}'.format( n+1 )
							record[ key ] = value
						key = record['DocID']
						meta[ key ] = record
			return sorted(header), meta
		except:
			return None, None
	
	def SaveMetaToDisk( self, meta ):
		self.logger.info( '    Writing data to disk: %s', self.app_data_path )
		if meta is not None:
			filename = '{}/doc-meta.json'.format( self.app_data_path )
			with open( filename, 'w' ) as f:
				json.dump( meta, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def SaveMetaToDB( self, meta, header ):
		def CreateTable():
			columnDefs = [ [ f ] for f in header ]
			for i, columnDef in enumerate(columnDefs):
				column = header[i]
				if column.lower() == 'year':
					columnDef.append( 'INTEGER' )
				else:
					columnDef.append( 'STRING' )
				if column.lower() == 'docid':
					columnDef.append( 'UNIQUE' )
				columnDef.append( 'NOT NULL' )
					
			columnDefs = ', '.join( [ ' '.join(d) for d in columnDefs ] )
			sql = """CREATE TABLE IF NOT EXISTS {TABLE} ( Key INTEGER PRIMARY KEY AUTOINCREMENT, {COLUMN_DEFS} );""".format( TABLE = table, COLUMN_DEFS = columnDefs )
			conn.execute( sql )
		def InsertData():
			columns = ', '.join( header )
			values = ', '.join( [ '?' for f in header ] )
			sql = """INSERT OR IGNORE INTO {TABLE} ( {COLUMNS} ) VALUES( {VALUES} )""".format( TABLE = table, COLUMNS = columns, VALUES = values )
			data = []
			for d in meta.itervalues():
				data.append( [ d[f] for f in header ] )
			conn.executemany( sql, data )
			
		self.logger.info( '    Writing data to database: %s', self.app_data_path )
		if meta is not None and header is not None:
			table = 'DocMeta'
			filename = '{}/doc-meta.sqlite'.format( self.app_data_path )
			
			conn = sqlite3.connect( filename )
			CreateTable()
			InsertData()
			conn.commit()
			conn.close()
	
	def ImportTerms( self, filename, minFreq = 5, minDocFreq = 2, maxCount = 1000 ):
		self.logger.info( 'Computing term frequencies and co-occurrences...' )
		corpus = self.ExtractCorpusTerms( filename )
		termFreqs, termDocFreqs = self.ComputeTermFreqs( corpus )
		termCoFreqs, termCoFreqOptions = self.ComputeTermCoFreqs( corpus, termFreqs, termDocFreqs, minFreq, minDocFreq, maxCount )
		self.SaveTermsToDisk( termFreqs, termDocFreqs, termCoFreqs, termCoFreqOptions )
	
	def ExtractCorpusTerms( self, filename ):
		self.logger.info( '    Reading mallet corpus: %s', filename )
		process = subprocess.Popen( "java -jar {} {}".format( CORPUS_WRITER, filename ), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True )
		( out, err ) = process.communicate()
		self.logger.info( err )
		corpus = {}
		for document in out.splitlines():
			docID, docTokens = document.split( '\t' )
			corpus[ docID ] = docTokens.split( ' ' )
		return corpus
	
	def ComputeTermFreqs( self, corpus ):
		self.logger.info( '    Computing term freqs...' )
		termFreqs = {}
		termDocFreqs = {}
		for docID, docTokens in corpus.iteritems():
			for token in docTokens:
				if token not in termFreqs:
					termFreqs[ token ] = 1
				else:
					termFreqs[ token ] += 1
			uniqueTokens = frozenset( docTokens )
			for token in uniqueTokens:
				if token not in termDocFreqs:
					termDocFreqs[ token ] = 1
				else:
					termDocFreqs[ token ] += 1
		return termFreqs, termDocFreqs

	def ComputeTermCoFreqs( self, corpus, termFreqs, termDocFreqs, minFreq, minDocFreq, maxCount ):
		def getTokenPairs( firstToken, secondToken ):
			if firstToken < secondToken:
				return firstToken, secondToken
			else:
				return secondToken, firstToken
				
		self.logger.info( '    Computing term co-occurrences...' )
		keys = set()
		for term in termFreqs:
			if termFreqs[term] >= minFreq:
				if termDocFreqs[term] >= minDocFreq:
					keys.add(term)
		keys = sorted( keys, key = lambda x : -termFreqs[x] )
		keys = keys[:maxCount]
		keySet = frozenset(keys)
		termCoFreqs = {}
		for docID, docTokens in corpus.iteritems():
			n = len(docTokens)
			for i in range(n):
				firstToken = docTokens[i]
				if firstToken in keySet:
					for j in range(i+1,n):
						secondToken = docTokens[j]
						if secondToken in keySet:
							a, b = getTokenPairs( firstToken, secondToken )
							if a not in termCoFreqs:
								termCoFreqs[a] = { 'b' : 1 }
							elif b not in termCoFreqs[a]:
								termCoFreqs[a][b] = 1
							else:
								termCoFreqs[a][b] += 1
		options = {
			'minFreq' : minFreq,
			'minDocFreq' : minDocFreq,
			'maxCount' : maxCount,
			'keys' : keys
		}
		return termCoFreqs, options
		
	def SaveTermsToDisk( self, termFreqs, termDocFreqs, termCoFreqs, termCoFreqOptions ):
		self.logger.info( 'Writing data to disk: %s', self.app_data_path )
		filename = '{}/term-freqs.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( termFreqs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-doc-freqs.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( termDocFreqs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-co-freqs.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoFreqs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-co-freq-options.json'.format( self.app_data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoFreqOptions, f, encoding = 'utf-8', indent = 2, sort_keys = True )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name'  , type = str,                 help = 'Web2py application identifier'                                     )
	parser.add_argument( '--meta'    , type = str, default = None, help = 'Import document metadata from a tab-delimited file'                )
	parser.add_argument( '--terms'   , type = str, default = None, help = 'Calculate term freqs and co-occurrences from a corpus.mallet file' )
	args = parser.parse_args()
	
	importer = ImportCorpus( app_name = args.app_name )
	if args.meta is not None:
		importer.ImportMeta( args.meta )
	if args.terms is not None:
		importer.ImportTerms( args.terms )
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
