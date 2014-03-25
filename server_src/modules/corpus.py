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
		docIndex = self.GetParam("docIndex")
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
		searchText = self.GetParam("searchText")
		searchLimit = self.GetParam("searchLimit")
		searchOffset = self.GetParam("searchOffset")
		filename = os.path.join( self.request.folder, 'data/corpus', 'documents-meta.json' )
		with open( filename ) as f:
			corpus = json.load( f, encoding = 'utf-8' )
			corpusHeader = corpus['header']
			corpusData = corpus['data']
		documents = {}
		matchCount = 0
		for docID, document in corpusData.iteritems():
			docContent = document['DocContent']
			if re.search( searchText, docContent ) is not None:
				matchCount += 1
				if searchOffset <= matchCount and matchCount < searchOffset + searchLimit:
					documents[ docID ] = document
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
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			allTermFreqs = termStats['freqs']
		allTerms = sorted( allTermFreqs.iterkeys(), key = lambda x : -allTermFreqs[x] )
		termMaxCount = len(allTerms)
		subTerms = allTerms[termOffset:termOffset+termLimit]
		termCount = len(subTerms)
		subTermFreqs = { term : allTermFreqs[term] for term in subTerms }
		results = {
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount,
			'TermFreqs' : subTermFreqs
		}
		self.content.update(results)
		return results

	def LoadTermCoFreqs( self ):
		self.LoadTermFreqs()
		termSet = frozenset( self.content['TermFreqs'].iterkeys() )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermCoFreqs = termCoStats['coFreqs']
		subTermCoFreqs = { term : allTermCoFreqs[term] for term in termSet if term in allTermCoFreqs }
		for term, termFreqs in subTermCoFreqs.iteritems():
			subTermCoFreqs[ term ] = { t : termFreqs[t] for t in termSet if t in termFreqs }
		results = {
			'TermCoFreqs' : subTermCoFreqs
		}
		self.content.update(results)
		return results

	def LoadTermProbs( self ):
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			allTermProbs = termStats['probs']
		allTerms = sorted( allTermProbs.iterkeys(), key = lambda x : -allTermProbs[x] )
		termMaxCount = len(allTerms)
		subTerms = allTerms[termOffset:termOffset+termLimit]
		termCount = len(subTerms)
		subTermProbs = { term : allTermProbs[term] for term in subTerms }
		results = {
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermCount' : termCount,
			'TermMaxCount' : termMaxCount,
			'TermProbs' : subTermProbs
		}
		self.content.update(results)
		return results

	def LoadTermCoProbs( self ):
		self.LoadTermProbs()
		termSet = frozenset( self.content['TermProbs'].iterkeys() )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermCoProbs = termCoStats['coProbs']
		subTermCoProbs = { term : allTermCoProbs[term] for term in termSet if term in allTermCoProbs }
		for term, termProbs in subTermCoProbs.iteritems():
			subTermCoProbs[ term ] = { t : termProbs[t] for t in termSet if t in termProbs }
		results = {
			'TermCoProbs' : subTermCoProbs
		}
		self.content.update(results)
		return results

	def LoadTermPMI( self ):
		self.LoadTermProbs()
		termSet = frozenset( self.content['TermProbs'].iterkeys() )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermPMI = termCoStats['pmi']
		subTermPMI = { term : allTermPMI[term] for term in termSet if term in allTermPMI }
		for term, termProbs in subTermPMI.iteritems():
			subTermPMI[ term ] = { t : termProbs[t] for t in termSet if t in termProbs }
		results = {
			'TermPMI' : subTermPMI
		}
		self.content.update(results)
		return results
