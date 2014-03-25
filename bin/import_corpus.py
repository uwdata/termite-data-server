#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import json
import sqlite3
from import_abstr import ImportAbstraction
from corpus.CorpusReader import CorpusReader
from corpus.MetaReader import MetaReader
from corpus.SentenceReader import SentenceReader

STOPWORDS = 'tools/mallet/stoplists/en.txt'

class ImportCorpus( ImportAbstraction ):
	
	def __init__( self, app_name, app_model = 'corpus', app_desc = 'Corpus Metadata and Statistics' ):
		ImportAbstraction.__init__( self, app_name, app_model, app_desc )
		self.stopwords = []
		with open( STOPWORDS ) as f:
			self.stopwords = f.read().decode('utf-8', 'ignore').splitlines()
	
	def ImportDocMeta( self, filename, fromCorpus = False ):
		print 'Importing document metadata...'
		print '    Reading document metadata: {}'.format( filename )
		reader = MetaReader( filename, stopwords = self.stopwords, fromCorpus = fromCorpus )
		meta = { docID : docMeta for docID, docMeta in reader.Load() }
		header = reader.header
		self.SaveDocMetaToDisk( header, meta )
		self.SaveDocMetaToDB( header, meta )
	
	def SaveDocMetaToDisk( self, header, meta ):
		print '    Writing data to disk: {}'.format( self.data_path )
		if meta is not None and header is not None:
			filename = '{}/documents-meta.json'.format( self.data_path )
			with open( filename, 'w' ) as f:
				data = { "header" : header, "data" : meta }
				json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def SaveDocMetaToDB( self, header, meta ):
		def CreateTable():
			columnDefs = [ [ field['name'] ] for field in header ]
			for i, field in enumerate(header):
				columnDef = columnDefs[i]
				if field['type'] == 'int':
					columnDef.append('INTEGER')
				else:
					columnDef.append('STRING')
				if field['name'] == 'DocID':
					columnDef.append('UNIQUE')
				columnDef.append('NOT NULL')
			columnDefs = ', '.join( [ ' '.join(d) for d in columnDefs ] )
			sql = """CREATE TABLE IF NOT EXISTS {TABLE} ( Key INTEGER PRIMARY KEY AUTOINCREMENT, {COLUMN_DEFS} );""".format( TABLE = table, COLUMN_DEFS = columnDefs )
			conn.execute( sql )
		def InsertData():
			columns = ', '.join( [ field['name'] for field in header ] )
			values = ', '.join( [ '?' for field in header ] )
			sql = """INSERT OR IGNORE INTO {TABLE} ( {COLUMNS} ) VALUES( {VALUES} )""".format( TABLE = table, COLUMNS = columns, VALUES = values )
			data = []
			for d in meta.itervalues():
				data.append( [ d[field['name']] for field in header ] )
			conn.executemany( sql, data )
			
		print '    Writing data to database: {}'.format( self.database_path )
		if meta is not None and header is not None:
			table = 'DocMeta'
			filename = '{}/documents-meta.sqlite'.format( self.database_path )
			conn = sqlite3.connect( filename )
			CreateTable()
			InsertData()
			conn.commit()
			conn.close()
	
	def ImportCorpusStats( self, filename, minFreq = 5, minDocFreq = 2, maxCount = 1000 ):
		print 'Computing document-level term statistics...' 
		print '    Reading text corpus: {}'.format( filename )
		reader = CorpusReader( filename, stopwords = self.stopwords )
		corpus = { docID : docContent for docID, docContent in reader.Load() }
		termStats, termFreqs, termProbs, termDocFreqs = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termFreqs, termProbs, termDocFreqs, minFreq, minDocFreq, maxCount )
		termFreqSortedList, termTfIdfSortedList = self.CompileTermKeys( termStats )
		self.SaveCorpusStatsToDisk( termStats, termCoStats, termFreqSortedList, termTfIdfSortedList )
	
	def ImportSentenceStats( self, filename, minFreq = 5, minDocFreq = 2, maxCount = 1000 ):
		print 'Computing sentence-level term statistics...'
		print '    Reading text corpus: {}'.format( filename )
		reader = SentenceReader( filename, stopwords = self.stopwords )
		corpus = { docID+":"+docSubID : docContent for docID, docSubID, docContent in reader.Load() }
		termStats, termFreqs, termProbs, termDocFreqs = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termFreqs, termProbs, termDocFreqs, minFreq, minDocFreq, maxCount )
		termFreqSortedList, termTfIdfSortedList = self.CompileTermKeys( termStats )
		self.SaveSentenceStatsToDisk( termStats, termCoStats, termFreqSortedList, termTfIdfSortedList )
	
	def ComputeTermFreqs( self, corpus ):
		print '    Computing term freqs ({})...'.format( len(corpus) )
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

		# Normalize to create a probability distribution
		normalization = sum( termFreqs.itervalues() )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		termProbs = { term : termFreqs[term] * normalization for term in termFreqs.iterkeys() }

		N = len(corpus)
		termTfIdfs = { term : termFreqs[term] * math.log(1.0*N/termDocFreqs[term]) for term in termFreqs.iterkeys() }
		
		termStats = {
			'freqs' : termFreqs,
			'probs' : termProbs,
			'docFreqs' : termDocFreqs,
			'tfIdfs' : termTfIdfs
		}
		return termStats, termFreqs, termProbs, termDocFreqs

	def ComputeTermCoFreqs( self, corpus, termFreqs, termProbs, termDocFreqs, minFreq, minDocFreq, maxCount ):
		def getTokenPairs( firstToken, secondToken ):
			if firstToken < secondToken:
				return firstToken, secondToken
			else:
				return secondToken, firstToken
				
		print '    Computing term co-occurrences ({})...'.format( len(corpus) )
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
								termCoFreqs[a] = { b : 1 }
							elif b not in termCoFreqs[a]:
								termCoFreqs[a][b] = 1
							else:
								termCoFreqs[a][b] += 1

		# Normalize to create joint probability distribution
		normalization = sum( sum( d.itervalues() ) for d in termCoFreqs.itervalues() )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		termCoProbs = { term : { t : f * normalization for t, f in termFreqs.iteritems() } for term, termFreqs in termCoFreqs.iteritems() }
		
		termPMI = {}
		for x, probs in termCoProbs.iteritems():
			termPMI[x] = {}
			for y, prob in probs.iteritems():
				if x in termProbs and y in termProbs:
					termPMI[x][y] = prob / termProbs[x] / termProbs[y]
				else:
					termPMI[x][y] = 0.0
		
		termCoStats = {
			'coFreqs' : termCoFreqs,
			'coProbs' : termCoProbs,
			'pmi' : termPMI
		}
		return termCoStats
	
	def CompileTermKeys( self, termStats ):
		termFreqSortedList = sorted( termStats['freqs'].iterkeys(), key = lambda x : -termStats['freqs'][x] )
		termTfIdfSortedList = sorted( termStats['tfIdfs'].iterkeys(), key = lambda x : -termStats['tfIdfs'][x] )
		return termFreqSortedList, termTfIdfSortedList
		
	def SaveCorpusStatsToDisk( self, termStats, termCoStats, termFreqSortedList, termTfIdfSortedList ):
		print 'Writing data to disk: {}'.format( self.data_path )
		filename = '{}/corpus-term-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/corpus-term-co-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/key--corpus-term-freq.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			for term in termFreqSortedList:
				f.write( u'{}\n'.format(term).encode('utf-8') )
		filename = '{}/key--corpus-term-tfidf.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			for term in termTfIdfSortedList:
				f.write( u'{}\n'.format(term).encode('utf-8') )

	def SaveSentenceStatsToDisk( self, termStats, termCoStats, termFreqSortedList, termTfIdfSortedList ):
		print 'Writing data to disk: {}'.format( self.data_path )
		filename = '{}/sentence-term-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/sentence-term-co-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/key--sentence-term-freq.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			for term in termFreqSortedList:
				f.write( u'{}\n'.format(term).encode('utf-8') )
		filename = '{}/key--sentence-term-tfidf.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			for term in termTfIdfSortedList:
				f.write( u'{}\n'.format(term).encode('utf-8') )

def main():
	import argparse
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name', type = str, help = 'Web2py application identifier' )
	parser.add_argument( 'corpus'  , type = str, help = 'Import corpus from a file or folder' )
	parser.add_argument( 'meta'    , type = str, nargs = '?', default = None, help = 'Import document metadata from a tab-delimited file [with header and fields DocID and DocContent]' )
	args = parser.parse_args()
	
	importer = ImportCorpus( app_name = args.app_name )
	if importer.AddAppFolder():
		if args.meta is None:
			importer.ImportDocMeta( args.corpus, fromCorpus = True )
		else:
			importer.ImportDocMeta( args.meta )
		importer.ImportCorpusStats( args.corpus )
		importer.ImportSentenceStats( args.corpus )
		importer.AddToWeb2py()
	else:
		print "    Already available: {}".format( importer.app_path )

if __name__ == '__main__':
	main()
