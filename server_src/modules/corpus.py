#!/usr/bin/env python

import os
import json

class Corpus:
	def __init__( self, request ):
		self.request = request
		self.params = self.GetParams()
	
	def GetParams( self ):
		def GetNonNegativeInteger( key, defaultValue ):
			try:
				n = int( self.request.vars[ key ] )
				if n >= 0:
					return n
				else:
					return 0
			except:
				return defaultValue
		
		def GetString( key, defaultValue ):
			if key in self.request.vars:
				return self.request.vars[ key ]
			else:
				return defaultValue
		
		params = {
			'searchLimit' : GetNonNegativeInteger( 'searchLimit', 100 ),
			'searchOffset' : GetNonNegativeInteger( 'searchOffset', 0 ),
			'searchText' : GetString( 'searchText', '' ),
			'searchOrdering' : GetString( 'searchOrdering', '' ),
			'termLimit' : GetNonNegativeInteger( 'termLimit', 100 ),
			'termOffset' : GetNonNegativeInteger( 'termOffset', 0 )
		}
		return params
	
	def GetDocMeta( self, params = None ):
		if params is None:
			params = self.params
		searchText = params["searchText"]
		searchLimit = params["searchLimit"]
		searchOffset = params["searchOffset"]

		filename = os.path.join( self.request.folder, 'data/corpus', 'doc-meta.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )['data']
			results = {}
			matchCount = 0
			keys = sorted(content.keys())
			for index in range(len(keys)):
			    obj = content[keys[index]]
			    docContent = obj["DocContent"]
			    if searchText in docContent:
			        matchCount += 1
			        if len(results) < searchLimit and index >= searchOffset:
			           results[obj["DocID"]] = obj
		return {
			"Documents" : results,
			"docCount" : len(results),
			"docMaxCount" : matchCount
		}

	def GetTermFreqs( self, params = None ):
		if params is None:
			params = self.params
		termLimit = params['termLimit']
		termOffset = params['termOffset']

		filename = os.path.join( self.request.folder, 'data/corpus', 'term-freqs.json' )
		with open( filename ) as f:
			allTermFreqs = json.load( f, encoding = 'utf-8' )
		allTerms = sorted( allTermFreqs.keys(), key = lambda x : -allTermFreqs[x] )
		terms = allTerms[termOffset:termOffset+termLimit]
		termFreqs = { term : allTermFreqs[term] for term in terms if term in allTermFreqs }
		return termFreqs

	def GetTermCoFreqs( self, params = None ):
		if params is None:
			params = self.params
		termLimit = params['termLimit']
		termOffset = params['termOffset']

		filename = os.path.join( self.request.folder, 'data/corpus', 'term-freqs.json' )
		with open( filename ) as f:
			allTermFreqs = json.load( f, encoding = 'utf-8' )
		allTerms = sorted( allTermFreqs.keys(), key = lambda x : -allTermFreqs[x] )
		terms = allTerms[termOffset:termOffset+termLimit]
		
		filename = os.path.join( self.request.folder, 'data/corpus', 'term-co-freqs.json' )
		with open( filename ) as f:
			allTermCoFreqs = json.load( f, encoding = 'utf-8' )
		termCoFreqs = { term : allTermCoFreqs[term] for term in terms if term in allTermCoFreqs }
		for term, termFreqs in termCoFreqs.iteritems():
			termCoFreqs[ term ] = { t : termFreqs[t] for t in terms if t in termFreqs }
		return termCoFreqs
