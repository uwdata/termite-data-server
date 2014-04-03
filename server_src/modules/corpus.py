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
		# Parameters
		docIndex = self.GetParam('docIndex')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'documents-meta.json' )
		with open( filename ) as f:
			corpus = json.load( f, encoding = 'utf-8' )
			corpusHeader = corpus['header']
			corpusData = corpus['data']
		if docIndex in corpusData:
			document = corpusData[docIndex]
		else:
			document = None
			
		# Responses
		self.content.update({
			'Document' : document,
			'DocIndex' : docIndex
		})
		self.table = [ document ]
		self.header = corpusHeader
	
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
		
		# Processing
		documents = []
		matchCount = 0
		for docID, document in corpusData.iteritems():
			docContent = document['DocContent']
			if re.search( searchText, docContent ) is not None:
				matchCount += 1
				if searchOffset < matchCount and matchCount <= searchOffset + searchLimit:
					documents.append( document )
		matchMaxCount = len(documents)
		
		# Responses
		self.content.update({
			'Documents' : documents,
			'DocCount' : matchMaxCount,
			'DocMaxCount' : matchCount
		})
		self.table = documents
		self.header = corpusHeader

	def LoadTermFreqs( self ):
		# Parameters
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		
		# Load from disk
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			fullTable = termStats['freqs']
		
		# Processing
		vocab = sorted( fullTable.iterkeys(), key = lambda x : -fullTable[x] )
		vocab = vocab[ termOffset:termOffset+termLimit ]
		table = [ { 'term' : term, 'freq' : fullTable[term] } for term in vocab ]
		header = [
			{ 'name' : 'term', 'type' : 'string' },
			{ 'name' : 'freq', 'type' : 'number' }
		]
		termMaxCount = len(fullTable)
		termCount = len(table)
		
		# Responses
		self.content.update({
			'TermFreqs' : table,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount,
			'Vocab' : vocab
		})
		self.table = table
		self.header = header

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
		table = [ { 'term' : term, 'prob' : fullTable[term] } for term in vocab ]
		header = [
			{ 'name' : 'term', 'type' : 'string' },
			{ 'name' : 'prob', 'type' : 'number' }
		]
		termMaxCount = len(fullTable)
		termCount = len(table)

		# Responses
		self.content.update({
			'TermProbs' : table,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount,
			'Vocab' : vocab
		})
		self.table = table
		self.header = header

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
		header = [
			{ 'name' : 'firstTerm', 'type' : 'string' },
			{ 'name' : 'secondTerm', 'type' : 'string' },
			{ 'name' : 'freq', 'type' : 'number' }
		]
		
		# Responses
		self.content.update({
			'TermCoFreqs' : table
		})
		self.table = table
		self.header = header

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
		header = [
			{ 'name' : 'firstTerm', 'type' : 'string' },
			{ 'name' : 'secondTerm', 'type' : 'string' },
			{ 'name' : 'prob', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TermCoProbs' : table
		})
		self.table = table
		self.header = header

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
		header = [
			{ 'name' : 'firstTerm', 'type' : 'string' },
			{ 'name' : 'secondTerm', 'type' : 'string' },
			{ 'name' : 'pmi', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TermPMI' : table
		})
		self.table = table
		self.header = header

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
		header = [
			{ 'name' : 'firstTerm', 'type' : 'string' },
			{ 'name' : 'secondTerm', 'type' : 'string' },
			{ 'name' : 'pmi', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TermSentencePMI' : table
		})
		self.table = table
		self.header = header

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
		header = [
			{ 'name' : 'firstTerm', 'type' : 'string' },
			{ 'name' : 'secondTerm', 'type' : 'string' },
			{ 'name' : 'g2', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TermG2' : table
		})
		self.table = table
		self.header = header

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
		header = [
			{ 'name' : 'firstTerm', 'type' : 'string' },
			{ 'name' : 'secondTerm', 'type' : 'string' },
			{ 'name' : 'g2', 'type' : 'number' }
		]

		# Responses
		self.content.update({
			'TermSentenceG2' : table
		})
		self.table = table
		self.header = header
