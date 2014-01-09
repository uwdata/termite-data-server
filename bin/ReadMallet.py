#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import math
import json

TOPIC_WORD_WEIGHTS = 'topic-word-weights.txt'
DOC_TOPIC_MIXTURES = 'doc-topic-mixtures.txt'

class ReadMallet( object ):
	def __init__( self, model_path, data_path, logging_level ):
		self.model_path = model_path
		self.data_path = data_path
		self.lda_path = self.data_path + '/data/lda'
		self.logger = logging.getLogger( 'ReadMallet' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	def execute( self, filenameTopicWordWeights, filenameDocTopicMixtures ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Importing a Mallet model...'                                                      )
		self.logger.info( '       model = %s', self.model_path                                               )
		self.logger.info( '         app = %s', self.data_path                                                )
		self.logger.info( '         lda = %s', self.lda_path                                                 )
		self.logger.info( ' topic-words = %s', filenameTopicWordWeights                                      )
		self.logger.info( '  doc-topics = %s', filenameDocTopicMixtures                                      )
		
		if not os.path.exists( self.lda_path ):
			self.logger.info( 'Making output folder: %s', self.lda_path )
			os.makedirs( self.lda_path )
		
		self.docs = set()
		self.terms = set()
		self.topics = set()
		self.docIDs = {}
		self.termFreqs = {}
		self.topicFreqs = {}
		self.docsAndTopics = {}
		self.topicsAndTerms = {}
		
		self.logger.info( 'Reading topic-term matrix from MALLET: %s', filenameTopicWordWeights )
		self.ExtractTopicWordWeights( filenameTopicWordWeights )

		self.logger.info( 'Reading doc-topic matrix from MALLET: %s', filenameDocTopicMixtures )
		self.ExtractDocTopicMixtures( filenameDocTopicMixtures )

		self.logger.info( 'Packaing data...' )
		self.Package()
		
		self.logger.info( 'Writing data to disk...' )
		self.SaveToDisk()
		
		self.logger.info( '--------------------------------------------------------------------------------' )
	
	def ExtractTopicWordWeights( self, filename ):
		terms = set()
		topics = set()
		termFreqs = {}
		topicFreqs = {}
		topicsAndTerms = {}
		
		filename = '{}/{}'.format( self.model_path, filename )
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				topic, term, value = line.split( '\t' )
				topic = int( topic, 10 )
				value = float( value )
				if topic not in topics:
					topics.add( topic )
					topicFreqs[ topic ] = 0.0
					topicsAndTerms[ topic ] = {}
				if term not in self.terms:
					terms.add( term )
					termFreqs[ term ] = 0.0

				topicsAndTerms[ topic ][ term ] = value
				topicFreqs[ topic ] += value
				termFreqs[ term ] += value
		
		self.terms = terms
		self.topics = topics
		self.termFreqs = termFreqs
		self.topicFreqs = topicFreqs
		self.topicsAndTerms = topicsAndTerms
	
	def ExtractDocTopicMixtures( self, filename ):
		docs = set()
		topics = set()
		docIDs = {}
		topicFreqs = {}
		docsAndTopics = {}

		filename = '{}/{}'.format( self.model_path, filename )
		header = None
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				if header is None:
					header = line
				else:
					fields = line.split( '\t' )
					doc = int(fields[0])
					docID = fields[1]
					topicKeys = [ int(field) for n, field in enumerate(fields[2:]) if n == 0 ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n == 1 ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if doc not in docs:
							docs.add( doc )
							docIDs[ doc ] = docID
							docsAndTopics[ doc ] = {}
						if topic not in topics:
							topics.add( topic )
							topicFreqs[ topic ] = 0.0
						docsAndTopics[ doc ][ topic ] = value
						topicFreqs[ topic ] += value
		
		self.docs = docs
		self.docIDs = docIDs
		self.docsAndTopics = docsAndTopics
		assert( len(self.topics) == len(topics) )
		assert( len(self.topicFreqs) == len(topicFreqs) )
	
	def Package( self ):
		self.docs = sorted( self.docs )
		self.terms = sorted( self.terms )
		self.topics = sorted( self.topics )
		self.docIndex = [ None ] * len( self.docs )
		self.termIndex = [ None ] * len( self.terms )
		self.topicIndex = [ None ] * len( self.topics )
		self.termTopicMatrix = [ None ] * len( self.terms )
		self.docTopicMatrix = [ None ] * len( self.docs )
		
		for n, doc in enumerate( self.docs ):
			self.docIndex[n] = {
				'index' : doc,
				'path' : self.docIDs[doc]
			}
		for n, term in enumerate( self.terms ):
			self.termIndex[n] = {
				'index' : n,
				'text' : term
			}
		for n, topic in enumerate( self.topics ):
			self.topicIndex[n] = {
				'index' : topic,
				'freq' : self.topicFreqs[topic]
			}
		for n, term in enumerate( self.terms ):
			row = [ 0.0 ] * len( self.topics )
			for topic in self.topics:
				if topic in self.topicsAndTerms and term in self.topicsAndTerms[ topic ]:
					row[ topic ] = self.topicsAndTerms[ topic ][ term ]
			self.termTopicMatrix[ n ] = row
		for doc in self.docs:
			row = [ 0.0 ] * len( self.topics )
			for topic, value in self.docsAndTopics[ doc ].iteritems():
				row[ topic ] = value
			self.docTopicMatrix[ doc ] = row
		
	def SaveToDisk( self ):
		filename = '{}/doc-index.json'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-index.txt'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			f.write( u'{}\t{}\n'.format( 'DocIndex', 'DocPath' ) )
			for d in self.docIndex:
				f.write( u'{}\t{}\n'.format( d['index'], d['path'] ) )

		filename = '{}/term-index.json'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.txt'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			f.write( u'{}\n'.format( 'TermIndex', 'TermText' ) )
			for d in self.termIndex:
				f.write( u'{}\n'.format( d['index'], d['text'] ).encode( 'utf-8' ) )
			
		filename = '{}/topic-index.json'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.txt'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			f.write( u'{}\t{}\n'.format( 'TopicIndex', 'TopicFreq' ) )
			for d in self.topicIndex:
				f.write( u'{}\t{}\n'.format( d['index'], d['freq'] ).encode( 'utf-8' ) )

		filename = '{}/term-topic-matrix.txt'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			for row in self.termTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )

		filename = '{}/doc-topic-matrix.txt'.format( self.lda_path )
		with open( filename, 'w' ) as f:
			for row in self.docTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'model_path'   , type = str,               help = 'MALLET topic model path.'                                              )
	parser.add_argument( 'data_path'    , type = str,               help = 'Web2py application path.'                                              )
	parser.add_argument( '--topic_words', type = str, default = TOPIC_WORD_WEIGHTS, help = 'File containing topic vs. word weights.'               )
	parser.add_argument( '--doc_topics' , type = str, default = DOC_TOPIC_MIXTURES, help = 'File containing doc vs. topic mixtures.'               )
	parser.add_argument( '--logging'    , type = int, default = 20, help = 'Override default logging level.'                                       )
	args = parser.parse_args()
	
	ReadMallet(
		model_path = args.model_path, 
		data_path = args.data_path, 
		logging_level = args.logging
	).execute(
		args.topic_words, 
		args.doc_topics
	)

if __name__ == '__main__':
	main()
