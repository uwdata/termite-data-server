#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class CommonLDA( object ):
	
	def __init__( self ):
		pass
		
	def ResolveMatrices( self ):
		"""
		Generate term-topic and doc-topic matrices (if needed)
		Combine a 2D array term-topic-matrix.txt file with the term-index.json files.
		Generate the required term-topic-matrix.json file.
		Similarly for doc-topic-matrix.json file.
		"""
		index_filename = '{}/term-index.json'.format( self.data_path )
		original_filename = '{}/term-topic-matrix.txt'.format( self.data_path )
		resolved_filename = '{}/term-topic-matrix.json'.format( self.data_path )
		with open( index_filename, 'r' ) as f:
			index = json.load( f, encoding = 'utf-8' )
		with open( original_filename, 'r' ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		resolved = self.ResolveMatrix( matrix, [ d['text'] for d in index ] )
		with open( resolved_filename, 'w' ) as f:
			json.dump( resolved, f, encoding = 'utf-8', indent = 2, sort_keys = True )

		index_filename = '{}/doc-index.json'.format( self.data_path )
		original_filename = '{}/doc-topic-matrix.txt'.format( self.data_path )
		resolved_filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		with open( index_filename, 'r' ) as f:
			index = json.load( f, encoding = 'utf-8' )
		with open( original_filename, 'r' ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		resolved = self.ResolveMatrix( matrix, [ d['docID'] for d in index ] )
		with open( resolved_filename, 'w' ) as f:
			json.dump( resolved, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def ResolveMatrix( self, matrix, keys ):
		resolved = {}
		assert len( matrix ) == len( keys )
		for i, key in enumerate( keys ):
			resolved[ key ] = matrix[ i ]
		return resolved
		
	def TransposeMatrices( self ):
		"""
		Generate topic-term matrix from term-topic matrix.
		Generate topic-doc matrix from doc-topic matrix.
		"""
		original_filename = '{}/term-topic-matrix.json'.format( self.data_path )
		transposed_filename = '{}/topic-term-matrix.json'.format( self.data_path )
		with open( original_filename, 'r' ) as f:
			termsAndTopics = json.load( f, encoding = 'utf-8' )
		topicsAndTerms = self.TransposeMatrix( termsAndTopics )
		with open( transposed_filename, 'w' ) as f:
			json.dump( topicsAndTerms, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		original_filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		transposed_filename = '{}/topic-doc-matrix.json'.format( self.data_path )
		with open( original_filename, 'r' ) as f:
			docsAndTopics = json.load( f, encoding = 'utf-8' )
		topicsAndDocs = self.TransposeMatrix( docsAndTopics )
		with open( transposed_filename, 'w' ) as f:
			json.dump( topicsAndDocs, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def TransposeMatrix( self, matrix ):
		transposed = []
		for key, values in matrix.iteritems():
			for index, value in enumerate( values ):
				while len( transposed ) <= index:
					transposed.append( {} )
				transposed[ index ][ key ] = value
		return transposed

	def ComputeTopicCooccurrenceAndCovariance( self ):
		filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		with open( filename, 'r' ) as f:
			docsAndTopics = json.load( f, encoding = 'utf-8' )
		docCount = len(docsAndTopics)
		topicCount = max([0] + [len(d) for d in docsAndTopics.itervalues()])
		
		self.logger.info( 'Computing topic cooccurrence...' )
		matrix = [ [0.0] * topicCount for _ in range(topicCount) ]
		for docID, topicMixture in docsAndTopics.iteritems():
			for i in range(topicCount):
				for j in range(topicCount):
					matrix[i][j] += topicMixture[i] * topicMixture[j]
		self.topicCooccurrence = [ [ matrix[i][j] / docCount for j in range(topicCount) ] for i in range(topicCount) ]

		self.logger.info( 'Computing topic covariance...' )
		normalization = sum( sum(d) for d in matrix )
		normalization = 1.0 / normalization if normalization > 1.0 else 1.0
		self.topicCovariance = [ [ matrix[i][j] * normalization for j in range(topicCount) ] for i in range(topicCount) ]

		filename = '{}/topic-cooccurrence.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicCooccurrence, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-covariance.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicCovariance, f, encoding = 'utf-8', indent = 2, sort_keys = True )
