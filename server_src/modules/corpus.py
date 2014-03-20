#!/usr/bin/env python

import os
import json
from core import TermiteCore

class Corpus( TermiteCore ):
	def __init__( self, request, response ):
		super( Corpus, self ).__init__( request, response )

	def GetParam( self, key ):
		if key == 'searchLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'searchLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'searchLimit', 5 )
			self.params.update({ key : value })

		elif key == 'searchOffset':
			value = self.GetNonNegativeIntegerParam( 'searchOffset', 0 )
			self.params.update({ key : value })

		elif key == 'termLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'termLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'termLimit', 5 )
			self.params.update({ key : value })

		elif key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( 'termOffset', 0 )
			self.params.update({ key : value })

		elif key == 'searchText':
			value = self.GetStringParam( 'searchText', '' )
			self.params.update({ key : value })

		return value
	
	def LoadDocMeta( self ):
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
			keys = sorted(content.iterkeys())
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

	def LoadTermFreqs( self ):
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		filename = os.path.join( self.request.folder, 'data/corpus', 'term-freqs.json' )
		with open( filename ) as f:
			allTermFreqs = json.load( f, encoding = 'utf-8' )
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
		filename = os.path.join( self.request.folder, 'data/corpus', 'term-co-freqs.json' )
		with open( filename ) as f:
			allTermCoFreqs = json.load( f, encoding = 'utf-8' )
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
		filename = os.path.join( self.request.folder, 'data/corpus', 'term-freqs.json' )
		with open( filename ) as f:
			allTermFreqs = json.load( f, encoding = 'utf-8' )
		normalization = sum( allTermFreqs.itervalues() )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		allTerms = sorted( allTermFreqs.iterkeys(), key = lambda x : -allTermFreqs[x] )
		termMaxCount = len(allTerms)
		subTerms = allTerms[termOffset:termOffset+termLimit]
		termCount = len(subTerms)
		subTermProbs = { term : allTermFreqs[term] * normalization for term in subTerms }
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
		filename = os.path.join( self.request.folder, 'data/corpus', 'term-co-freqs.json' )
		with open( filename ) as f:
			allTermCoFreqs = json.load( f, encoding = 'utf-8' )
		normalization = sum( [ sum( d.itervalues() ) for d in allTermCoFreqs.itervalues() ] )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		subTermCoProbs = { term : allTermCoFreqs[term] for term in termSet if term in allTermCoFreqs }
		for term, termFreqs in subTermCoProbs.iteritems():
			subTermCoProbs[ term ] = { t : termFreqs[t] * normalization for t in termSet if t in termFreqs }
		results = {
			'TermCoProbs' : subTermCoProbs
		}
		self.content.update(results)
		return results

	def LoadTermPMI( self ):
		self.LoadTermCoProbs()
		termProbs = self.content['TermProbs']
		termCoProbs = self.content['TermCoProbs']
		termPMI = {}
		for x, probs in termCoProbs.iteritems():
			termPMI[x] = {}
			for y, prob in probs.iteritems():
				if x in termProbs and y in termProbs:
					termPMI[x][y] = prob / termProbs[x] / termProbs[y]
				else:
					termPMI[x][y] = 0.0
		results = {
			'TermPMI' : termPMI
		}
		self.content.update(results)
		return results
		