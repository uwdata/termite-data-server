#!/usr/bin/env python

import os
import json
from core import TermiteCore
from json import encoder as JsonEncoder

class GroupInABox( TermiteCore ):
	def __init__( self, request, response ):
		super( GroupInABox, self ).__init__( request, response )
		JsonEncoder.FLOAT_REPR = lambda number : format( number, '.4g' )

	def GetParam( self, key ):
		if key == 'termLimit':
			if self.IsJsonFormat():
				value = self.GetNonNegativeIntegerParam( 'termLimit', 100 )
			else:
				value = self.GetNonNegativeIntegerParam( 'termLimit', 5 )
			self.params.update({ key : value })

		return value

	def LoadTopTermsPerTopic( self ):
		termLimit = self.GetParam('termLimit')
		filename = os.path.join( self.request.folder, 'data/lda', 'topic-term-matrix.json' )
		with open( filename ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		submatrix = []
		vocab = set()
		for vector in matrix:
			allTerms = sorted( vector.iterkeys(), key = lambda x : -vector[x] )
			subTerms = allTerms[:termLimit]
			termSet = frozenset(subTerms)
			vocab.update( termSet )
			submatrix.append( [ { term : vector[term] } for term in termSet if term in vector ] )
		results = {
			'TopTermsPerTopic' : submatrix,
			'Vocab' : list( vocab )
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
		vocab = frozenset( self.content['Vocab'] )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			allTermFreqs = termStats['freqs']
		subTermFreqs = { term : allTermFreqs[term] for term in vocab if term in allTermFreqs }
		results = {
			'TermFreqs' : subTermFreqs
		}
		self.content.update(results)
		return results

	def LoadTermCoFreqs( self ):
		vocab = frozenset( self.content['Vocab'] )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermCoFreqs = termCoStats['coFreqs']
		subTermCoFreqs = { term : allTermCoFreqs[term] for term in vocab if term in allTermCoFreqs }
		for term, termFreqs in subTermCoFreqs.iteritems():
			subTermCoFreqs[ term ] = { t : termFreqs[t] for t in vocab if t in termFreqs }
		results = {
			'TermCoFreqs' : subTermCoFreqs
		}
		self.content.update(results)
		return results

	def LoadTermProbs( self ):
		vocab = frozenset( self.content['Vocab'] )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-stats.json' )
		with open( filename ) as f:
			termStats = json.load( f, encoding = 'utf-8' )
			allTermProbs = termStats['probs']
		subTermProbs = { term : allTermProbs[term] for term in vocab if term in allTermProbs }
		results = {
			'TermProbs' : subTermProbs
		}
		self.content.update(results)
		return results

	def LoadTermCoProbs( self ):
		vocab = frozenset( self.content['Vocab'] )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermCoProbs = termCoStats['coProbs']
		subTermCoProbs = { term : allTermCoProbs[term] for term in vocab if term in allTermCoProbs }
		for term, termProbs in subTermCoProbs.iteritems():
			subTermCoProbs[ term ] = { t : termProbs[t] for t in vocab if t in termProbs }
		results = {
			'TermCoProbs' : subTermCoProbs
		}
		self.content.update(results)
		return results

	def LoadTermPMI( self ):
		vocab = frozenset( self.content['Vocab'] )
		filename = os.path.join( self.request.folder, 'data/corpus', 'corpus-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermPMI = termCoStats['coProbs']
		subTermPMI = { term : allTermPMI[term] for term in vocab if term in allTermPMI }
		for term, termProbs in subTermPMI.iteritems():
			subTermPMI[ term ] = { t : termProbs[t] for t in vocab if t in termProbs }
		results = {
			'TermPMI' : subTermPMI
		}
		self.content.update(results)
		return results

	def LoadTermSentencePMI( self ):
		vocab = frozenset( self.content['Vocab'] )
		filename = os.path.join( self.request.folder, 'data/corpus', 'sentence-term-co-stats.json' )
		with open( filename ) as f:
			termCoStats = json.load( f, encoding = 'utf-8' )
			allTermSentencePMI = termCoStats['coProbs']
		subTermSentencePMI = { term : allTermSentencePMI[term] for term in vocab if term in allTermSentencePMI }
		for term, termProbs in subTermSentencePMI.iteritems():
			subTermSentencePMI[ term ] = { t : termProbs[t] for t in vocab if t in termProbs }
		results = {
			'TermSentencePMI' : subTermSentencePMI
		}
		self.content.update(results)
		return results
