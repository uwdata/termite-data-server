#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class ReadTreeTM:
	
	ROOT = 'data'
	def Convert( self, dataID, entryID ):
		states = self._ReadStatesFile_( dataID, entryID )
		terms = states['rowLabels']
		topics = states['columnLabels']
		_, entries = self._ReadModelTopicsFile_( dataID, entryID, terms )
		if terms is not None:
			self._WriteTerms_( dataID, entryID, terms )
		if topics is not None:
			self._WriteTopics_( dataID, entryID, topics )
		if entries is not None:
			self._WriteTermTopicEntries_( dataID, entryID, entries )
		
	def _ReadStatesFile_( self, dataID, entryID ):
		filename = '{}/{}/entry-{:04d}/states.json'.format( self.ROOT, dataID, entryID )
		with open( filename ) as f:
			return json.load( f, encoding = 'utf-8' )
		
	def _ReadModelTopicsFile_( self, dataID, entryID, terms ):
		lookup = {}
		for index, term in enumerate(terms):
			lookup[ term ] = index

		filename = '{}/{}/entry-{:04d}/model.topics'.format( self.ROOT, dataID, entryID )
		try:
			with open( filename ) as f:
				topicLabels = []
				topicTermProbs = []
				topicIndex = -1
				mode = None
				for line in f.read().decode( 'utf-8' ).splitlines():
					if len(line) == 0:
						topicIndex += 1
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
#						if freq > 1e-6:
						topicTermProbs.append({ 'rowIndex' : lookup[term], 'columnIndex' : topicIndex, 'value' : freq })
		except IOError:
			topicLabels = None
			topicTermProbs = None
		return topicLabels, topicTermProbs

	def _WriteTerms_( self, dataID, entryID, terms ):
		filename = '{}/{}/entry-{:04d}/term-index.txt'.format( self.ROOT, dataID, entryID )
		with open( filename, 'w' ) as f:
			for term in terms:
				f.write( u'{}\n'.format( term ).encode( 'utf-8' ) )

	def _WriteTopics_( self, dataID, entryID, topics ):
		filename = '{}/{}/entry-{:04d}/topic-index.txt'.format( self.ROOT, dataID, entryID )
		with open( filename, 'w' ) as f:
			for topic in topics:
				f.write( u'{}\n'.format( topic ).encode( 'utf-8' ) )

	def _WriteTermTopicEntries_( self, dataID, entryID, entries ):
		filename = '{}/{}/entry-{:04d}/term-topic-entries.txt'.format( self.ROOT, dataID, entryID )
		with open( filename, 'w' ) as f:
			for entry in entries:
				f.write( u'{}\t{}\t{}\n'.format( entry['rowIndex'], entry['columnIndex'], entry['value'] ) )
