#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import math
from import_abstr import ImportAbstraction

class ImportTreeTM( ImportAbstraction ):
	
	def __init__( self, model_path, apps_root, app_name = 'lda', app_desc = 'Tree-TM' ):
		ImportAbstraction.__init__( self, app_name, app_model, app_desc )

	def ImportLDA( model_path ):
		latest_run = self.GetLatestRun()
		self.run_path = self.GetRunPath( model_path, latest_run )
		
		termList = self.ReadVocabFile( model_path )
		topicSet, termsAndTopics = self.ReadModelTopicsFile()
		self.SaveToDisk( termList, topicSet, termsAndTopics )

	def GetLatestRun( self, model_path ):
		latest_run = -1
		for filename in os.listdir( model_path ):
			path = '{}/{}'.format( model_path, filename )
			if os.path.isdir( path ):
				n = int( filename )
				latest_run = max( latest_run, n )
		return latest_run

	def GetRunPath( self, model_path, iter ):
		return '{}/{:06d}'.format( model_path, iter )

	def ReadVocabFile( self, model_path ):
		filename = '{}/corpus.voc'.format( model_path )
		with open( filename ) as f:
			termList = [ line.split( '\t' )[1] for line in f.read().splitlines() ]
		return termList

	def ReadModelTopicsFile( self ):
		print 'Reading model.topics file: {}/{}'.format( model_path, 'model.topics' )
		lookup = { n : term for n, term in enumerate( self.terms ) }
		filename = '{}/model.topics'.format( self.run_path )
		topicSet = set()
		termsAndTopics = {}
		try:
			with open( filename ) as f:
				topicLabels = []
				topicTermProbs = []
				topicIndex = -1
				topicStr = None
				mode = None
				for line in f.read().decode( 'utf-8' ).splitlines():
					if len(line) == 0:
						topicIndex += 1
						topicSet.add( topicIndex )
						continue
					if line == '--------------':
						mode = 'topic'
						continue
					if line == '------------------------':
						mode = 'term'
						continue
					if mode == 'topic':
						topicLabels.append( line )
						continue
					if mode == 'term':
						freq, term = line.split( '\t' )
						freq = float( freq )
						if term not in termsAndTopics:
							termsAndTopics[ term ] = {}
						termsAndTopics[ term ][ topicIndex ] = freq
		except IOError:
			pass
		return topicSet, termsAndTopics

	def SaveToDisk( self, termList, topicSet, termsAndTopics ):
		print 'Writing data to disk: {}'.format( self.data_path )
		docs = []
		terms = termList
		topics = sorted( topicSet, key = lambda x : int(x) )
		docIndex = []
		docIndex = [ None ] * len( docs )
		termIndex = [ None ] * len( terms )
		topicIndex = [ None ] * len( topics )
		for n, term in enumerate( terms ):
			termIndex[n] = {
				'text' : term
			}
		for n, doc in enumerate( docs ):
			docIndex[n] = {
				'docID' : doc
			}
		for n, topic in enumerate( topics ):
			topicIndex[n] = {
				'index' : topic
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
		filename = '{}/term-topic-matrix.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( termsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		filename = '{}/doc-topic-matrix.txt'.format( self.data_path )
		with open( filename, 'w' ) as f:
			json.dump( docsAndTopics, f, encoding = 'utf-8', indent = 2, sort_keys = True )

		self.docs = docs
		self.terms = terms
		self.topics = topics
		self.termsAndTopics = termsAndTopics
		self.docsAndTopics = docsAndTopics
	
def main():
	parser = argparse.ArgumentParser( description = 'Import a tree topic model as a web2py application.' )
	parser.add_argument( 'model_path'   , type = str,                               help = 'Tree topic model path.'                  )
	parser.add_argument( 'app_name'     , type = str,                               help = 'Web2py application identifier'           )
	args = parser.parse_args()
	
	importer = ImportTreeTM( apps_root = args.apps_root, app_name = args.app_name )
	if importer.AddAppFolder():
		importer.ImportLDA( args.model_path )
		importer.AddToWeb2py()
	else:
		print "    Already available: {}".format( importer.app_path )

if __name__ == '__main__':
	main()
