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
		dictionary, model = self.ExtractGensimModel( dictionary_filename, model_filename )
		self.SaveToDisk( dictionary, model )
	
	def ExtractGensimModel( self, dictionary_filename, model_filename ):
		print 'Reading from {}, {}'.format( dictionary_filename, model_filename )
		dictionary = corpora.Dictionary.load( dictionary_filename )
		model = models.LdaModel.load( model_filename )
		return dictionary, model
	
	def SaveToDisk( self, dictionary, model ):
		termTexts = {}
		for i in dictionary:
			termTexts[i] = dictionary[i]
		topics = model.show_topics( topics = -1, topn = len(termTexts), formatted = False )

		docIndex = []
		termIndex = [ None ] * len( termTexts )
		topicIndex = [ None ] * len( topics )
		termsAndTopics = {}
		docsAndTopics = {}

		for termID, termText in termTexts.iteritems():
			termIndex[termID] = {
				'index' : termID,
				'text' : termText,
				'docFreq' : dictionary.dfs[termID]
			}
			termsAndTopics[ termText ] = [ 0.0 ] * len( topics )
		for n, topic in enumerate( topics ):
			topicIndex[n] = {
				'index' : n
			}
			for freq, termText in topic:
				termsAndTopics[ termText ][ n ] = freq

		print 'Writing data to disk: {}'.format( self.data_path )
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

def main():
	parser = argparse.ArgumentParser( description = 'Import a Gensim topic model as a web2py application.' )
	parser.add_argument( 'app_name'  , type = str, help = 'Web2py application identifier'                  )
	parser.add_argument( 'dictionary', type = str, help = 'File containing a gensim dictionary'            )
	parser.add_argument( 'model'     , type = str, help = 'File containing a gensim LDA model'             )
	args = parser.parse_args()
	
	importer = ImportGensim( args.app_name )
	importer.ImportLDA( args.dictionary, args.model )
	importer.TransposeMatrices()
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
