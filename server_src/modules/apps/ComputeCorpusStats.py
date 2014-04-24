#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
import re
from collections import Counter

class ComputeCorpusStats():
	
	DEFAULT_STOPWORDS = 'tools/mallet/stoplists/en.txt'
	
	def __init__( self, ldaDB, corpusStatsDB, corpusFilename, sentencesFilename, tokenRegex = r'\w{3,}', minFreq = 5, minDocFreq = 2, maxTermCount = 2500, maxCoTermCount = 25000, STOPWORDS = None ):
		self.logger = logging.getLogger('termite')
		self.ldaDB = ldaDB
		self.corpusStatsDB = corpusStatsDB
		self.corpusFilename = corpusFilename
		self.sentencesFilename = sentencesFilename
		self.tokenRegex = re.compile(tokenRegex)
		
		self.minFreq = minFreq
		self.minDocFreq = minDocFreq
		self.maxTermCount = maxTermCount
		self.maxCoTermCount = maxCoTermCount
		self.stopwords = self.LoadStopwords( STOPWORDS if STOPWORDS is not None else ComputeCorpusStats.DEFAULT_STOPWORDS )
	
	def Execute( self ):
		self.ReadTermLookup()
		self.ComputeAndSaveDocumentLevelStatistics()
		self.ComputeAndSaveSentenceLevelStatistics()
	
	def LoadStopwords( self, filename ):
		stopwords = []
		with open( filename, 'r' ) as f:
			stopwords = f.read().decode('utf-8', 'ignore').splitlines()
		return frozenset(stopwords)
	
	def ReadCorpus( self, filename ):
		self.logger.debug( '    Reading corpus: %s', filename )
		with open( filename, 'r' ) as f:
			for line in f:
				docID, docContent = line.decode('utf-8').rstrip('\n').split('\t')
				docTokens = self.tokenRegex.findall(docContent)
				docTokens = [ token.lower() for token in docTokens if token not in self.stopwords ]
				yield docID, docTokens
	
	def ReadTermLookup( self ):
		self.logger.debug( '    Loading terms...' )
		lookup = {}
		for row in self.ldaDB.db( self.ldaDB.db.terms ).select( self.ldaDB.db.terms.term_index, self.ldaDB.db.terms.term_text ):
			lookup[ row.term_text ] = row.term_index
		self.termLookup = lookup
	
	def UnfoldTermLookup( self ):
		data = []
		for term in self.vocab:
			if term in self.termLookup:
				index = self.termLookup[term]
				data.append({ 'term_index' : index, 'term_text' : term })
		return data
	
	def UnfoldStats( self, stats ):
		data = []
		for term in self.vocab:
			if term in stats and term in self.termLookup:
				index = self.termLookup[term]
				data.append({ 'term_index' : index, 'value' : stats[term] })
		data.sort( key = lambda x : -x['value'] )
		return data
	
	def UnfoldCoStats( self, coStats ):
		data = []
		for first_term, stats in coStats.iteritems():
			if first_term in self.termLookup:
				first_term_index = self.termLookup[first_term]
				for second_term, value in stats.iteritems():
					if second_term in self.termLookup:
						second_term_index = self.termLookup[second_term]
						data.append({ 'first_term_index' : first_term_index, 'second_term_index' : second_term_index, 'value' : value })
		data.sort( key = lambda x : -x['value'] )
		return data[:self.maxCoTermCount]
	
	def ComputeAndSaveDocumentLevelStatistics( self ):
		reader = self.ReadCorpus( self.corpusFilename )
		corpus = { docID : docTokens for docID, docTokens in reader }
		
		self.logger.info( 'Computing document-level statistics...' )
		termStats = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termStats )
		
		self.logger.debug( '    Saving term_texts...' )
		self.corpusStatsDB.db.term_texts.bulk_insert( self.UnfoldTermLookup() )
		self.logger.debug( '    Saving term_freqs...' )
		self.corpusStatsDB.db.term_freqs.bulk_insert( self.UnfoldStats(termStats['term_freqs']) )
		self.logger.debug( '    Saving term_probs...' )
		self.corpusStatsDB.db.term_probs.bulk_insert( self.UnfoldStats(termStats['term_probs']) )
		self.logger.debug( '    Saving term_doc_freqs...' )
		self.corpusStatsDB.db.term_doc_freqs.bulk_insert( self.UnfoldStats(termStats['term_doc_freqs']) )
		self.logger.debug( '    Saving term_co_freqs...' )
		self.corpusStatsDB.db.term_co_freqs.bulk_insert( self.UnfoldCoStats(termCoStats['co_freqs']) )
		self.logger.debug( '    Saving term_co_probs...' )
		self.corpusStatsDB.db.term_co_probs.bulk_insert( self.UnfoldCoStats(termCoStats['co_probs']) )
		self.logger.debug( '    Saving term_pmi...' )
		self.corpusStatsDB.db.term_pmi.bulk_insert( self.UnfoldCoStats(termCoStats['pmi']) )
		self.logger.debug( '    Saving term_g2...' )
		self.corpusStatsDB.db.term_g2.bulk_insert( self.UnfoldCoStats(termCoStats['g2']) )
	
	def ComputeAndSaveSentenceLevelStatistics( self ):
		reader = self.ReadCorpus( self.sentencesFilename )
		corpus = { docID : docTokens for docID, docTokens in reader }
		
		self.logger.info( 'Computing sentence-level term statistics...' )
		termStats = self.ComputeTermFreqs( corpus )
		termCoStats = self.ComputeTermCoFreqs( corpus, termStats )
		
		self.logger.debug( '    Saving sentences_co_freqs...' )
		self.corpusStatsDB.db.sentences_co_freqs.bulk_insert( self.UnfoldCoStats(termCoStats['co_freqs']) )
		self.logger.debug( '    Saving sentences_co_probs...' )
		self.corpusStatsDB.db.sentences_co_probs.bulk_insert( self.UnfoldCoStats(termCoStats['co_probs']) )
		self.logger.debug( '    Saving sentences_pmi...' )
		self.corpusStatsDB.db.sentences_pmi.bulk_insert( self.UnfoldCoStats(termCoStats['pmi']) )
		self.logger.debug( '    Saving sentences_g2...' )
		self.corpusStatsDB.db.sentences_g2.bulk_insert( self.UnfoldCoStats(termCoStats['g2']) )
	
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
#		termIdfs = ComputeIdfs( corpus, termDocFreqs )
#		termTfIdfs = ComputeTfIdfs( termFreqs, termIdfs )
		
		termStats = {
			'term_freqs' : termFreqs,
			'term_probs' : termProbs,
			'term_doc_freqs' : termDocFreqs
		}
#		termStats = {
#			'term_freq' : termFreqs,
#			'term_prob' : termProbs,
#			'term_doc_freq' : termDocFreqs,
#			'term_idf' : termIdfs,
#			'term_tfidf' : termTfIdfs
#		}
		return termStats
	
	def ComputeTermCoFreqs( self, corpus, termStats ):
		minFreq = self.minFreq
		minDocFreq = self.minDocFreq
		maxTermCount = self.maxTermCount
		termFreqs = termStats['term_freqs']
		termProbs = termStats['term_probs']
		termDocFreqs = termStats['term_doc_freqs']
		
		def GetVocab( termFreqs, termDocFreqs, minFreq, minDocFreq, maxTermCount ):
			keys = [ term for term in termFreqs if termFreqs[term] >= minFreq and termDocFreqs[term] >= minDocFreq ]
			keys = sorted( keys, key = lambda x : -termFreqs[x] )
			keys = keys[:maxTermCount]
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
		self.vocab = GetVocab( termFreqs, termDocFreqs, minFreq, minDocFreq, maxTermCount )
		
		# Count co-occurrences
		termCoFreqs, allFreq, allCoFreq = ComputeJointFreqs( corpus, self.vocab )
		
		# Normalize to create joint probability distribution
		termCoProbs = NormalizeJointFreqs( termCoFreqs, 1.0 / allCoFreq if allCoFreq > 1.0 else 1.0 )
		
		# Compute pointwise mutual information from marginal/joint probability distributions
		termPMI = ComputePMI( termProbs, termCoProbs )
		
		# Compute G2 statistics
		termG2 = ComputeG2Stats( allFreq, termProbs, termCoProbs )
		
		termCoStats = {
			'co_freqs' : termCoFreqs,
			'co_probs' : termCoProbs,
			'pmi' : termPMI,
			'g2' : termG2
		}
		return termCoStats
