#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import math
from import_abstr import ImportAbstraction

TOPIC_WORD_WEIGHTS = 'topic-word-weights.txt'
DOC_TOPIC_MIXTURES = 'doc-topic-mixtures.txt'

class ImportMallet( ImportAbstraction ):
	
	def __init__( self, app_name, app_model = 'lda', app_desc = 'LDA Topic Model' ):
		ImportAbstraction.__init__( self, app_name, app_model, app_desc )

	def ImportLDA( self, model_path, filenameTopicWordWeights, filenameDocTopicMixtures ):
		termSet, topicSet, termFreqs, topicFreqs, termsAndTopics = self.ExtractTopicWordWeights( model_path, filenameTopicWordWeights )
		docSet, _, docsAndTopics = self.ExtractDocTopicMixtures( model_path, filenameDocTopicMixtures, len(topicSet) )
		self.SaveToDisk( termSet, docSet, topicSet, termFreqs, topicFreqs, termsAndTopics, docsAndTopics )
	
	def ExtractTopicWordWeights( self, model_path, filename ):
		print 'Reading topic-term matrix: {}/{}'.format( model_path, filename )
		termSet = set()
		topicSet = set()
		termFreqs = {}
		topicFreqs = []
		termsAndTopics = {}
		filename = '{}/{}'.format( model_path, filename )
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				topic, term, value = line.split( '\t' )
				topic = int( topic )
				value = float( value )
				if topic not in topicSet:
					topicSet.add( topic )
					topicFreqs.append( 0.0 )
				if term not in termSet:
					termSet.add( term )
					termFreqs[ term ] = 0.0
					termsAndTopics[ term ] = []
				termsAndTopics[ term ].append( value )
				topicFreqs[ topic ] += value
				termFreqs[ term ] += value
		return termSet, topicSet, termFreqs, topicFreqs, termsAndTopics
	
	def ExtractDocTopicMixtures( self, model_path, filename, topicCount ):
		print 'Reading doc-topic matrix: {}/{}'.format( model_path, filename )
		docSet = set()
		topicSet = set()
		docsAndTopics = {}
		filename = '{}/{}'.format( model_path, filename )
		header = None
		with open( filename, 'r' ) as f:
			lines = f.read().decode( 'utf-8' ).splitlines()
			for line in lines:
				if header is None:
					header = line
				else:
					fields = line.split( '\t' )
					docID = fields[1]
					topicKeys = [ int(key) for n, key in enumerate(fields[2:]) if n % 2 == 0 and key != '' ]
					topicValues = [ float(value) for n, value in enumerate(fields[2:]) if n % 2 == 1 and value != '' ]
					for n in range(len(topicKeys)):
						topic = topicKeys[n]
						value = topicValues[n]
						if topic not in topicSet:
							topicSet.add( topic )
						if docID not in docSet:
							docSet.add( docID )
							docsAndTopics[ docID ] = [ 0.0 ] * topicCount
						docsAndTopics[ docID ][ topic ] = value
		return docSet, topicSet, docsAndTopics
	
	def SaveToDisk( self, termSet, docSet, topicSet, termFreqs, topicFreqs, termsAndTopics, docsAndTopics ):
		print 'Writing data to disk: {}'.format( self.data_path )
		docs = sorted( docSet )
		terms = sorted( termSet, key = lambda x : -termFreqs[x] )
		topics = sorted( topicSet )
		docIndex = [ None ] * len( docs )
		termIndex = [ None ] * len( terms )
		topicIndex = [ None ] * len( topics )
		for n, term in enumerate( terms ):
			termIndex[n] = {
				'text' : term,
				'freq' : termFreqs[ term ]
			}
		for n, doc in enumerate( docs ):
			docIndex[n] = {
				'docID' : doc
			}
		for n, topic in enumerate( topics ):
			topicIndex[n] = {
				'index' : topic,
				'freq' : topicFreqs[ topic ]
			}
		
		filename = '{}/doc-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-topic-matrix.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-topic-matrix.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( docsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		
		self.docs = docs
		self.terms = terms
		self.topics = topics
		self.termsAndTopics = termsAndTopics
		self.docsAndTopics = docsAndTopics

	def ImportTopicCooccurrence( self ):
		print 'Computing topic co-occurrence...'
		topics = self.topics
		matrix = [ [0.0]*len(topics) for i in range(len(topics)) ]
		for docID, topicMixture in self.docsAndTopics.iteritems():
			for i in topics:
				for j in topics:
					matrix[i][j] += topicMixture[i] * topicMixture[j]
		filename = '{}/topic-cooccurrence.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( matrix, f, encoding = 'utf-8', indent = 2, sort_keys = True )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name'     , type = str,                               help = 'Web2py application identifier'              )
	parser.add_argument( 'model_path'   , type = str,                               help = 'MALLET topic model path.'                   )
	parser.add_argument( '--topic_words', type = str, default = TOPIC_WORD_WEIGHTS, help = 'File containing topic vs. word weights.'    )
	parser.add_argument( '--doc_topics' , type = str, default = DOC_TOPIC_MIXTURES, help = 'File containing doc vs. topic mixtures.'    )
	args = parser.parse_args()
	
	importer = ImportMallet( app_name = args.app_name )
	if importer.AddAppFolder():
		importer.ImportLDA( args.model_path, args.topic_words, args.doc_topics )
		importer.ImportTopicCooccurrence()
		importer.TransposeMatrices()
		importer.AddToWeb2py()
	else:
		print "    Already available: {}".format( importer.app_path )

if __name__ == '__main__':
	main()
