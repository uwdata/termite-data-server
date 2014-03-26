#!/usr/bin/env python

import re
import os
import json
import operator
from core import TermiteCore

class Corpus( TermiteCore ):
	def __init__( self, request, response ):
		super( Corpus, self ).__init__( request, response )

	def GetParam( self, key ):
		if key == 'searchText':
			value = self.GetStringParam( 'searchText' )
			self.params.update({ key : value })

		if key == 'searchLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'searchLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'searchLimit', 5 )
			self.params.update({ key : value })

		if key == 'searchOffset':
			value = self.GetNonNegativeIntegerParam( 'searchOffset', 0 )
			self.params.update({ key : value })

		if key == 'termLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'termLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'termLimit', 5 )
			self.params.update({ key : value })

		if key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( 'termOffset', 0 )
			self.params.update({ key : value })

		if key == 'docIndex':
			value = self.GetStringParam( 'docIndex' )
			self.params.update({ key : value })

		return value
	
	def LoadDocument( self ):
		docIndex = self.GetParam('docIndex')
		filename = os.path.join( self.request.folder, 'data/corpus', 'documents-meta.json' )
		with open( filename ) as f:
			corpus = json.load( f, encoding = 'utf-8' )
			corpusHeader = corpus['header']
			corpusData = corpus['data']
		if docIndex in corpusData:
			document = corpusData[docIndex]
		else:
			document = None
		results = {
			'Document' : document,
			'DocIndex' : docIndex
		}
		self.content.update(results)
		return results
	
	def LoadTextSearch( self ):
		# Parameters
		searchText = self.GetParam('searchText')
		searchLimit = self.GetParam('searchLimit')
		searchOffset = self.GetParam('searchOffset')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'documents-meta.json' )
		with open( filename ) as f:
			corpus = json.load( f, encoding = 'utf-8' )
			corpusHeader = corpus['header']
			corpusData = corpus['data']
		documents = []
		matchCount = 0
		for docID, document in corpusData.iteritems():
			docContent = document['DocContent']
			if re.search( searchText, docContent ) is not None:
				matchCount += 1
				if searchOffset < matchCount and matchCount <= searchOffset + searchLimit:
					documents.append( document )
		
		# Responses
		results = {
			'Documents' : documents,
			'SearchText' : searchText,
			'SearchOffset' : searchOffset,
			'SearchLimit' : searchLimit,
			'MatchMaxCount' : matchCount,
			'MatchCount' : len(documents)
		}
		self.content.update(results)
		return results

	def LoadTermFreqs( self ):
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			allTermFreqs = termStats['freqs']
		termMaxCount = len(allTermFreqs)
		vocab = sorted( allTermFreqs.iterkeys(), key = lambda x : -allTermFreqs[x] )
		vocab = frozenset( vocab[ termOffset:termOffset+termLimit ] )
		termCount = len(vocab)
		table = [ { 'text' : term, 'freq' : allTermFreqs[term] } for term in vocab ]
		
		# Responses
		results = {
			'TermFreqs' : table,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermMaxCount' : termMaxCount,
			'TermCount' : termCount,
			'Vocab' : list(vocab)
		}
		self.content.update(results)
		return results

	def LoadTermProbs( self ):
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			allTermProbs = termStats['probs']
		termMaxCount = len(allTermProbs)
		vocab = sorted( allTermProbs.iterkeys(), key = lambda x : -allTermProbs[x] )
		vocab = frozenset( vocab[ termOffset:termOffset+termLimit ] )
		termCount = len(vocab)
		table = [ { 'text' : term, 'prob' : allTermProbs[term] } for term in vocab ]

		# Responses
		results = {
			'TermProbs' : table,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermMaxCount' : termMaxCount,
			'TermCount' : termCount,
			'Vocab' : list(vocab)
		}
		self.content.update(results)
		return results

	def LoadTermCoFreqs( self ):
		# Vocab
		self.LoadTermFreqs()
		vocab = frozenset( self.content['Vocab'] )

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermCoFreqs = termCoStats['coFreqs']
		table = []
		for term, termFreqs in allTermCoFreqs.iteritems():
			if term in vocab:
				table += [ { 'firstTerm' : term, 'secondTerm' : t, 'freq' : freq } for t, freq in termFreqs.iteritems() if t in vocab ]

		# Responses
		results = {
			'TermCoFreqs' : table
		}
		self.content.update(results)
		return results

	def LoadTermCoProbs( self ):
		# Vocab
		self.LoadTermProbs()
		vocab = frozenset( self.content['Vocab'] )

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermCoProbs = termCoStats['coProbs']
		table = []
		for term, termProbs in allTermCoProbs.iteritems():
			if term in vocab:
				table += [ { 'firstTerm' : term, 'secondTerm' : t, 'freq' : freq } for t, freq in termProbs.iteritems() if t in vocab ]

		# Responses
		results = {
			'TermCoProbs' : table
		}
		self.content.update(results)
		return results

	def LoadTermPMI( self ):
		# Vocab
		self.LoadTermProbs()
		vocab = frozenset( self.content['Vocab'] )

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermPMI = termCoStats['pmi']
		table = []
		for term, termProbs in allTermPMI.iteritems():
			if term in vocab:
				table += [ { 'firstTerm' : term, 'secondTerm' : t, 'freq' : freq } for t, freq in termProbs.iteritems() if t in vocab ]

		# Responses
		results = {
			'TermPMI' : table
		}
		self.content.update(results)
		return results

	def LoadTermSentencePMI( self ):
		# Vocab
		self.LoadTermProbs()
		vocab = frozenset( self.content['Vocab'] )

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'sentence-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermSentencePMI = termCoStats['pmi']
		table = []
		for term, termProbs in allTermSentencePMI.iteritems():
			if term in vocab:
				table += [ { 'firstTerm' : term, 'secondTerm' : t, 'freq' : freq } for t, freq in termProbs.iteritems() if t in vocab ]

		# Responses
		results = {
			'TermSentencePMI' : table
		}
		self.content.update(results)
		return results
