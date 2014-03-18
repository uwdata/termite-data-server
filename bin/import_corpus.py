#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sqlite3
import subprocess
from import_abstr import ImportAbstraction

CORPUS_WRITER = 'utils/mallet/CorpusWriter.jar'

class ImportCorpus( ImportAbstraction ):
	
	def __init__( self, app_name, app_model = 'corpus', app_desc = 'Corpus Metadata and Statistics' ):
		ImportAbstraction.__init__( self, app_name, app_model, app_desc )
	
	def ImportMeta( self, filename ):
		print 'Importing metadata...'
		header, meta = self.ExtractDocMeta( filename )
		self.SaveMetaToDisk( meta, header )
		self.SaveMetaToDB( meta, header )
		
	def ExtractDocMeta( self, filename ):
		print 'Reading document metadata: {}'.format( filename )
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
	
	def SaveMetaToDisk( self, meta, header ):
		print 'Writing data to disk: {}'.format( self.data_path )
		if meta is not None and header is not None:
			filename = '{}/doc-meta.json'.format( self.data_path )
			with open( filename, 'w' ) as f:
				data = { "header" : { h : ( "string" if h != 'Year' else 'integer' ) for h in header }, "data" : meta }
				json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )

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
			
		print 'Writing data to database: {}'.format( self.database_path )
		if meta is not None and header is not None:
			table = 'DocMeta'
			filename = '{}/doc-meta.sqlite'.format( self.database_path )
			
			conn = sqlite3.connect( filename )
			CreateTable()
			InsertData()
			conn.commit()
			conn.close()
	
	def ImportTerms( self, filename, minFreq = 5, minDocFreq = 2, maxCount = 1000 ):
		print 'Computing term frequencies and co-occurrences...' 
		corpus = self.ExtractCorpusTerms( filename )
		termFreqs, termDocFreqs = self.ComputeTermFreqs( corpus )
		termCoFreqs, termCoFreqOptions = self.ComputeTermCoFreqs( corpus, termFreqs, termDocFreqs, minFreq, minDocFreq, maxCount )
		self.SaveTermsToDisk( termFreqs, termDocFreqs, termCoFreqs, termCoFreqOptions )
	
	def ExtractCorpusTerms( self, filename ):
		print 'Reading mallet corpus: {}'.format( filename )
		command = [ "java", "-jar", CORPUS_WRITER, filename ]
		print ' '.join(command)
		process = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
		( out, err ) = process.communicate()
		print err
		corpus = {}
		for document in out.splitlines():
			docID, docTokens = document.split( '\t' )
			corpus[ docID ] = docTokens.split( ' ' )		
		return corpus
	
	def ComputeTermFreqs( self, corpus ):
		print 'Computing term freqs...'
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
				
		print 'Computing term co-occurrences...'
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
		print 'Writing data to disk: {}'.format( self.data_path )
		filename = '{}/term-freqs.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termFreqs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-doc-freqs.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termDocFreqs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-co-freqs.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoFreqs, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-co-freqs-options.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoFreqOptions, f, encoding = 'utf-8', indent = 2, sort_keys = True )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name', type = str,                 help = 'Web2py application identifier'                                     )
	parser.add_argument( '--meta'  , type = str, default = None, help = 'Import document metadata from a tab-delimited file'                )
	parser.add_argument( '--terms' , type = str, default = None, help = 'Calculate term freqs and co-occurrences from a corpus.mallet file' )
	args = parser.parse_args()
	
	importer = ImportCorpus( app_name = args.app_name )
	if args.meta is not None:
		importer.ImportMeta( args.meta )
	if args.terms is not None:
		importer.ImportTerms( args.terms )
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
