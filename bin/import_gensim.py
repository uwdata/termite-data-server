#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from gensim import corpora, models
from import_abstr import ImportAbstraction

class ImportGensim( ImportAbstraction ):
	
	def __init__( self, app_name, app_model = 'lda', app_desc = 'Gensim Topic Model' ):
		ImportAbstraction.__init__( self, app_name, app_model, app_desc )

	def ImportLDA( self, dictionary_filename, model_filename ):
		self.ExtractGensimModel( dictionary_filename, model_filename )
		self.SaveToDisk()
	
	def ExtractGensimModel( self, dictionary_filename, model_filename ):
		print 'Reading from {}, {}'.format( dictionary_filename, model_filename )
		termTexts = {}
		termLookup = {}
		dictionary = corpora.Dictionary.load( dictionary_filename )
		model = models.LdaModel.load( model_filename )
		for i in dictionary:
			termTexts[i] = dictionary[i]
			termLookup[dictionary[i]] = i
		topics = model.show_topics( topics = -1, topn = len(termTexts), formatted = False )

		self.docIndex = []
		self.termIndex = [ None ] * len( termTexts )
		self.topicIndex = [ None ] * len( topics )
		self.termTopicMatrix = [ None ] * len( termTexts )
		self.docTopicMatrix = []

		for termID, termText in termTexts.iteritems():
			self.termIndex[termID] = {
				'index' : termID,
				'text' : termText,
				'docFreq' : dictionary.dfs[termID]
			}
			self.termTopicMatrix[termID] = [ 0.0 ] * len( topics )
		for n, topic in enumerate( topics ):
			self.topicIndex[n] = {
				'index' : n
			}
			for freq, termText in topic:
				termID = termLookup[ termText ]
				self.termTopicMatrix[ termID ][ n ] = freq

	def SaveToDisk( self ):
		print 'Writing data to disk: {}'.format( self.data_path )
		filename = '{}/doc-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.docIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.termIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/topic-index.json'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( self.topicIndex, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/term-topic-matrix.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			for row in self.termTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )
		filename = '{}/doc-topic-matrix.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			for row in self.docTopicMatrix:
				f.write( u'{}\n'.format( '\t'.join( [ str( value ) for value in row ] ) ) )

def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'app_name'   , type = str,               help = 'Web2py application identifier'              )
	parser.add_argument( 'dictionary' , type = str,               help = 'File containing a gensim dictionary'        )
	parser.add_argument( 'model'      , type = str,               help = 'File containing a gensim LDA model'         )
	parser.add_argument( '--logging'  , type = int, default = 20, help = 'Override default logging level.'            )
	args = parser.parse_args()
	
	importer = ImportGensim( args.app_name )
	importer.ImportLDA( args.dictionary, args.model )
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
