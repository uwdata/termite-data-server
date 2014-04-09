#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import math
import os
from collections import Counter
from corpus.CorpusReader import CorpusReader
from corpus.MetaReader import MetaReader
from corpus.SentenceReader import SentenceReader

class Corpus( object ):
	
	DEFAULT_STOPWORDS = 'tools/mallet/stoplists/en.txt'

	def __init__( self, app_path, corpus_path, meta_path, minFreq = 5, minDocFreq = 2, maxVocabCount = 1000, STOPWORDS = None ):
		self.stopwords = self.LoadStopwords( STOPWORDS if STOPWORDS is not None else Corpus.DEFAULT_STOPWORDS)
		self.logger = logging.getLogger('termite')

		self.app_path = app_path
		self.data_path = '{}/data/corpus'.format( self.app_path )
		self.corpus_path = corpus_path
		self.meta_path = meta_path
		
		self.minFreq = minFreq
		self.minDocFreq = minDocFreq
		self.maxVocabCount = maxVocabCount

	def LoadStopwords( self, filename ):
		stopwords = []
		with open( filename, 'r' ) as f:
			stopwords = f.read().decode('utf-8', 'ignore').splitlines()
		return stopwords
	
	def Exists( self ):
		return os.path.exists( self.data_path )

	def Execute( self ):
		if not os.path.exists( self.data_path ):
			os.makedirs( self.data_path )

		self.ImportMetadata()
		self.ImportDocumentStats()
		self.ImportSentenceStats()
	
	def ImportMetadata( self ):
		metaData = None
		metaHeader = None
		
		if self.meta_path is None:
			self.logger.info( 'Reading text corpus: %s', self.corpus_path )
			reader = MetaReader( self.corpus_path, stopwords = self.stopwords, fromCorpus = True )
		else:
			self.logger.info( 'Reading document metadata: %s', self.meta_path )
			reader = MetaReader( self.meta_path, stopwords = self.stopwords, fromCorpus = False )
		metaData = { docID : docMeta for docID, docMeta in reader.Load() }
		metaHeader = reader.header
		
		for header in metaHeader:
			if header['type'] == 'integer':
				for d in metaData.itervalues():
					d[header['name']] = int(d[header['name']])
			if header['type'] == 'real':
				for d in metaData.itervalues():
					d[header['name']] = float(d[header['name']])
		
		self.logger.info( 'Writing document metadata: %s', self.data_path )
		filename = '{}/documents-meta.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			data = { "header" : metaHeader, "data" : metaData }
			json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )
	
	def ImportDocumentStats( self ):
		corpus = None
		termStats = None
		termCoStats = None
		
		self.logger.info( 'Reading text corpus: %s', self.corpus_path )
		reader = CorpusReader( self.corpus_path, stopwords = self.stopwords )
		corpus = { docID : docTokens for docID, docContent, docTokens in reader.Load() }
		
		self.logger.info( 'Computing document-level statistics...' )
		termStats = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termStats )
	
		self.logger.info( 'Writing document-level statistics to disk: %s', self.data_path )
		filename = '{}/corpus-term-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/corpus-term-co-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		
	def ImportSentenceStats( self ):
		corpus = None
		termStats = None
		termCoStats = None
		
		self.logger.info( 'Reading text corpus: %s', self.corpus_path )
		reader = SentenceReader( self.corpus_path, stopwords = self.stopwords )
		corpus = { docID+":"+docSubID : docTokens for docID, docSubID, docSentence, docTokens in reader.Load() }

		self.logger.info( 'Computing sentence-level term statistics...' )
		termStats = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termStats )
	
		self.logger.info( 'Writing sentence-level statistics to disk: %s', self.data_path )
		filename = '{}/sentence-term-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/sentence-term-co-stats.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termCoStats, f, encoding = 'utf-8', indent = 2, sort_keys = True )

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
			
		self.logger.info( '    Computing term freqs (%d)...', len(corpus) )
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

	def ComputeTermCoFreqs( self, corpus, termStats ):
		minFreq = self.minFreq
		minDocFreq = self.minDocFreq
		maxVocabCount = self.maxVocabCount
		termFreqs = termStats['freqs']
		termProbs = termStats['probs']
		termDocFreqs = termStats['docFreqs']
		
		def GetVocab( termFreqs, termDocFreqs, minFreq, minDocFreq, maxVocabCount ):
			keys = [ term for term in termFreqs if termFreqs[term] >= minFreq and termDocFreqs[term] >= minDocFreq ]
			keys = sorted( keys, key = lambda x : -termFreqs[x] )
			keys = keys[:maxVocabCount]
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
		
		self.logger.info( '    Computing term co-occurrences (%d)...', len(corpus) )
		vocab = GetVocab( termFreqs, termDocFreqs, minFreq, minDocFreq, maxVocabCount )

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
