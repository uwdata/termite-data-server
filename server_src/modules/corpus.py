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
			'searchOrdering' : GetString( 'searchOrdering', '' )
		}
		return params
	
	def GetDocMeta( self ):
		filename = os.path.join( self.request.folder, 'data/corpus', 'doc-meta.json' )
		with open( filename ) as f:
			content = json.load( f, encoding = 'utf-8' )
			
			# get self.params, setup results
			results = {}
			searchText = self.params["searchText"]
			searchLimit = self.params["searchLimit"]
			searchOffset = self.params["searchOffset"]
			
			matchCount = 0
			keys = sorted(content.keys())
			for index in range(len(keys)):
			    obj = content[keys[index]]
			    docContent = obj["DocContent"]
			    if searchText in docContent:
			        matchCount += 1
			        if len(results) < searchLimit and index >= searchOffset:
			           results[obj["DocID"]] = obj
		results = {
			"Documents" : results,
			"docCount" : len(results),
			"docMaxCount" : matchCount
		}
		return results
