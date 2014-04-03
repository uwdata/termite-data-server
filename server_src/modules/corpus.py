#!/usr/bin/env python

import re
import os
import json
from core import TermiteCore

class Corpus( TermiteCore ):
	def __init__( self, request, response ):
		super( Corpus, self ).__init__( request, response )

	def GetParam( self, key ):
		if key == 'searchText':
			value = self.GetStringParam( key )
			self.params.update({ key : value })
		if key == 'searchOffset':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		if key == 'searchLimit':
			if self.IsMachineFormat():
				value = self.GetNonNegativeIntegerParam( key, 50 )
			else:
				value = self.GetNonNegativeIntegerParam( key, 5 )
			self.params.update({ key : value })

		if key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( key, 0 )
			self.params.update({ key : value })
		if key == 'termLimit':
			if self.IsMachineFormat():
				value = self.GetNonNegativeIntegerParam( key, 50 )
			else:
				value = self.GetNonNegativeIntegerParam( key, 5 )
			self.params.update({ key : value })

		if key == 'docIndex':
			value = self.GetStringParam( key )
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
			'TextSearch' : documents,
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
			fullTable = termStats['freqs']
		termMaxCount = len(fullTable)
		vocab = sorted( fullTable.iterkeys(), key = lambda x : -fullTable[x] )
		vocab = vocab[ termOffset:termOffset+termLimit ]
		table = [ { 'text' : term, 'freq' : fullTable[term] } for term in vocab ]
		termCount = len(table)
		
		# Responses
		results = {
			'TermFreqs' : table,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermMaxCount' : termMaxCount,
			'TermCount' : termCount,
			'Vocab' : vocab
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
			fullTable = termStats['probs']
		termMaxCount = len(fullTable)
		vocab = sorted( fullTable.iterkeys(), key = lambda x : -fullTable[x] )
		vocab = vocab[ termOffset:termOffset+termLimit ]
		table = [ { 'text' : term, 'prob' : fullTable[term] } for term in vocab ]
		termCount = len(table)

		# Responses
		results = {
			'TermProbs' : table,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermMaxCount' : termMaxCount,
			'TermCount' : termCount,
			'Vocab' : vocab
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
			fullTable = termCoStats['coFreqs']
		table = []
		for firstTerm, d in fullTable.iteritems():
			if firstTerm in vocab:
				table += [ { 'firstTerm' : firstTerm, 'secondTerm' : secondTerm, 'freq' : value } for secondTerm, value in d.iteritems() if secondTerm in vocab ]
		table.sort( key = lambda x : -x['freq'] )
		
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
			fullTable = termCoStats['coProbs']
		table = []
		for firstTerm, d in fullTable.iteritems():
			if firstTerm in vocab:
				table += [ { 'firstTerm' : firstTerm, 'secondTerm' : secondTerm, 'prob' : value } for secondTerm, value in d.iteritems() if secondTerm in vocab ]
		table.sort( key = lambda x : -x['prob'] )

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
			fullTable = termCoStats['pmi']
		table = []
		for firstTerm, d in fullTable.iteritems():
			if firstTerm in vocab:
				table += [ { 'firstTerm' : firstTerm, 'secondTerm' : secondTerm, 'pmi' : value } for secondTerm, value in d.iteritems() if secondTerm in vocab ]
		table.sort( key = lambda x : -x['pmi'] )

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
			fullTable = termCoStats['pmi']
		table = []
		for firstTerm, d in fullTable.iteritems():
			if firstTerm in vocab:
				table += [ { 'firstTerm' : firstTerm, 'secondTerm' : secondTerm, 'pmi' : value } for secondTerm, value in d.iteritems() if secondTerm in vocab ]
		table.sort( key = lambda x : -x['pmi'] )

		# Responses
		results = {
			'TermSentencePMI' : table
		}
		self.content.update(results)
		return results

	def LoadTermG2( self ):
		# Vocab
		self.LoadTermProbs()
		vocab = frozenset( self.content['Vocab'] )

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			fullTable = termCoStats['g2']
		table = []
		for firstTerm, d in fullTable.iteritems():
			if firstTerm in vocab:
				table += [ { 'firstTerm' : firstTerm, 'secondTerm' : secondTerm, 'g2' : value } for secondTerm, value in d.iteritems() if secondTerm in vocab ]
		table.sort( key = lambda x : -x['g2'] )

		# Responses
		results = {
			'TermG2' : table
		}
		self.content.update(results)
		return results

	def LoadTermSentenceG2( self ):
		# Vocab
		self.LoadTermProbs()
		vocab = frozenset( self.content['Vocab'] )

		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'sentence-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			fullTable = termCoStats['g2']
		table = []
		for firstTerm, d in fullTable.iteritems():
			if firstTerm in vocab:
				table += [ { 'firstTerm' : firstTerm, 'secondTerm' : secondTerm, 'g2' : value } for secondTerm, value in d.iteritems() if secondTerm in vocab ]
		table.sort( key = lambda x : -x['g2'] )

		# Responses
		results = {
			'TermSentenceG2' : table
		}
		self.content.update(results)
		return results
