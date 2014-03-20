#!/usr/bin/env python

import os
import json
from core import TermiteCore

class GroupInABox( TermiteCore ):
	def __init__( self, request, response ):
		super( GroupInABox, self ).__init__( request, response )

	def GetParam( self, key ):
		if key == 'termLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'termLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'termLimit', 5 )
			self.params.update({ key : value })

		if key == 'termOffset':
			value = self.GetNonNegativeIntegerParam( 'termOffset', 0 )
			self.params.update({ key : value })

		return value

	def LoadTopTermsPerTopic( self ):
		termLimit = self.GetParam('termLimit')
		termOffset = self.GetParam('termOffset')
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = []
		for vector in matrix:
			allTerms = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subTerms = allTerms[termOffset:termOffset+termLimit]
			termSet = frozenset(subTerms)
			submatrix.append( { term : vector[term] for term in termSet if term in vector } )
		results = {
			'TopTermsPerTopic' : submatrix
		}
		self.content.update(results)
		return results

	def LoadTopicCooccurrence( self ):
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-cooccurrence.json' )
		with open( filename ) as f:
			topicCooccurrence = json.load( f, encoding = 'utf-8' )
		results = {
			'TopicCooccurrence' : topicCooccurrence
		}
		self.content.update(results)
		return results

	def LoadTopicCovariance( self ):
		self.LoadTopicCooccurrence()
		topicCooccurrence = self.content['TopicCooccurrence']
		normalization = sum( [ sum( vector ) for vector in topicCooccurrence ] )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		topicCovariance = [ [ value * normalization for value in vector ] for vector in topicCooccurrence ]
		results = {
			'TopicCovariance' : topicCovariance
		}
		self.content.update(results)
		return results

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
