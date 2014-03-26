#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import json
import sqlite3
from collections import Counter
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
		corpus = { docID : docTokens for docID, docContent, docTokens in reader.Load() }
		termStats = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termStats, minFreq, minDocFreq, maxCount )
		termFreqSortedList, termTfIdfSortedList = self.CompileTermKeys( termStats )
		self.SaveCorpusStatsToDisk( termStats, termCoStats, termFreqSortedList, termTfIdfSortedList )
	
	def ImportSentenceStats( self, filename, minFreq = 5, minDocFreq = 2, maxCount = 1000 ):
		print 'Computing sentence-level term statistics...'
		print '    Reading text corpus: {}'.format( filename )
		reader = SentenceReader( filename, stopwords = self.stopwords )
		corpus = { docID+":"+docSubID : docTokens for docID, docSubID, docSentence, docTokens in reader.Load() }
		termStats = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termStats, minFreq, minDocFreq, maxCount )
		termFreqSortedList, termTfIdfSortedList = self.CompileTermKeys( termStats )
		self.SaveSentenceStatsToDisk( termStats, termCoStats, termFreqSortedList, termTfIdfSortedList )
	
	def ComputeTermFreqs( self, corpus ):
		def ComputeFreqs( corpus ):
			freqs = Counter()
			for docID, docTokens in corpus.iteritems():
				freqs.update( docTokens )
			return freqs
		
		def ComputeDocFreqs( corpus ):
			docFreqs = Counter()
			for docID, docTokens in corpus.iteritems():
				uniqueTokens = frozenset( docTokens )
				docFreqs.update( uniqueTokens )
			return docFreqs
		
		def NormalizeFreqs( freqs ):
			normalization = sum( freqs.itervalues() )
			normalization = 1.0 / normalization if normalization > 1.0 else 1.0
			probs = { term : freq * normalization for term, freq in freqs.iteritems() }
			return probs
		
		def ComputeIdfs( corpus, docFreqs ):
			N = len( corpus )
			idfs = { term : math.log( 1.0 * N / docFreq ) for term, docFreq in docFreqs.iteritems() }
			return idfs
		
		def ComputeTfIdfs( freqs, idfs ):
			tfIdfs = { term : freq * idfs[term] for term, freq in freqs.iteritems() }
			return tfIdfs
			
		print '    Computing term freqs ({})...'.format( len(corpus) )
		termFreqs = ComputeFreqs( corpus )
		termDocFreqs = ComputeDocFreqs( corpus )
		termProbs = NormalizeFreqs( termFreqs )
		termIdfs = ComputeIdfs( corpus, termDocFreqs )
		termTfIdfs = ComputeTfIdfs( termFreqs, termIdfs )
		
		termStats = {
			'freqs' : termFreqs,
			'probs' : termProbs,
			'docFreqs' : termDocFreqs,
			'idfs' : termIdfs,
			'tfIdfs' : termTfIdfs
		}
		return termStats

	def ComputeTermCoFreqs( self, corpus, termStats, minFreq, minDocFreq, maxCount ):
		termFreqs = termStats['freqs']
		termProbs = termStats['probs']
		termDocFreqs = termStats['docFreqs']
		
		def GetVocab( termFreqs, termDocFreqs, minFreq, minDocFreq, maxCount ):
			keys = [ term for term in termFreqs if termFreqs[term] >= minFreq and termDocFreqs[term] >= minDocFreq ]
			keys = sorted( keys, key = lambda x : -termFreqs[x] )
			keys = keys[:maxCount]
			return frozenset(keys)
			
		def GetTokenPairs( firstToken, secondToken ):
			if firstToken < secondToken:
				return firstToken, secondToken
			else:
				return secondToken, firstToken

		def ComputeJointFreqs( corpus, vocab ):
			jointFreqs = {}
			allFreq = 0
			allCoFreq = 0
			for docID, docTokens in corpus.iteritems():
				freqs = Counter( docTokens )
				allFreq += sum( freqs.itervalues() )
				for firstToken, firstFreq in freqs.iteritems():
					for secondToken, secondFreq in freqs.iteritems():
						coFreq = firstFreq * secondFreq
						allCoFreq += coFreq
						if firstToken in vocab and secondToken in vocab and firstToken < secondToken:
							if firstToken not in jointFreqs:
								jointFreqs[firstToken] = { secondToken : coFreq }
							elif secondToken not in jointFreqs[firstToken]:
								jointFreqs[firstToken][secondToken] = coFreq
							else:
								jointFreqs[firstToken][secondToken] += coFreq
			return jointFreqs, allFreq, allCoFreq
		
		def NormalizeJointFreqs( jointFreqs, normalization = None ):
			if normalization is None:
				normalization = sum( sum( d.itervalues() ) for d in jointFreqs.itervalues() )
				normalization = 1.0 / normalization if normalization > 1.0 else 1.0
			jointProbs = { term : { t : f * normalization for t, f in freqs.iteritems() } for term, freqs in jointFreqs.iteritems() }
			return jointProbs

		def ComputePMI( marginalProbs, jointProbs ):
			pmi = {}
			for x, probs in jointProbs.iteritems():
				pmi[x] = {}
				for y, prob in probs.iteritems():
					if x in marginalProbs and y in marginalProbs:
						pmi[x][y] = prob / marginalProbs[x] / marginalProbs[y]
					else:
						pmi[x][y] = 0.0
			return pmi
		
		def GetBinomial( B_given_A, any_given_A, B_given_notA, any_given_notA ):
			assert B_given_A >= 0
			assert B_given_notA >= 0
			assert any_given_A >= B_given_A
			assert any_given_notA >= B_given_notA

			a = float( B_given_A )
			b = float( B_given_notA )
			c = float( any_given_A )
			d = float( any_given_notA )
			E1 = c * ( a + b ) / ( c + d )
			E2 = d * ( a + b ) / ( c + d )
			g2a = a * math.log( a / E1 ) if a > 0 else 0
			g2b = b * math.log( b / E2 ) if b > 0 else 0
			return 2 * ( g2a + g2b )

		def GetG2Stats( freq_all, freq_ab, freq_a, freq_b ):
			assert freq_all >= freq_a
			assert freq_all >= freq_b
			assert freq_a >= freq_ab
			assert freq_b >= freq_ab
			assert freq_all >= 0
			assert freq_ab >= 0
			assert freq_a >= 0
			assert freq_b >= 0

			B_given_A = freq_ab
			B_given_notA = freq_b - freq_ab
			any_given_A = freq_a
			any_given_notA = freq_all - freq_a
			return GetBinomial( B_given_A, any_given_A, B_given_notA, any_given_notA )

		def ComputeG2Stats( allFreq, marginalProbs, jointProbs ):
			g2_stats = {}
			freq_all = allFreq
			for firstToken, d in jointProbs.iteritems():
				g2_stats[ firstToken ] = {}
				for secondToken, jointProb in d.iteritems():
					freq_a = allFreq * marginalProbs[ firstToken ]
					freq_b = allFreq * marginalProbs[ secondToken ]
					freq_ab = allFreq * jointProb
					g2_stats[ firstToken ][ secondToken ] = GetG2Stats( freq_all, freq_ab, freq_a, freq_b )
			return g2_stats
		
		print '    Computing term co-occurrences ({})...'.format( len(corpus) )
		vocab = GetVocab( termFreqs, termDocFreqs, minFreq, minDocFreq, maxCount )

		# Count co-occurrences
		termCoFreqs, allFreq, allCoFreq = ComputeJointFreqs( corpus, vocab )
		
		# Normalize to create joint probability distribution
		termCoProbs = NormalizeJointFreqs( termCoFreqs, 1.0 / allCoFreq if allCoFreq > 1.0 else 1.0 )
		
		# Compute pointwise mutual information from marginal/joint probability distributions
		termPMI = ComputePMI( termProbs, termCoProbs )
		
		# Compute G2 statistics
		termG2 = ComputeG2Stats( allFreq, termProbs, termCoProbs )
		
		termCoStats = {
			'coFreqs' : termCoFreqs,
			'coProbs' : termCoProbs,
			'pmi' : termPMI,
			'g2' : termG2
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
