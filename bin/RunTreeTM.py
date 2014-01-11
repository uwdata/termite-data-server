#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import os.path

class RunTreeTM:
	
	ROOT = 'data'
	TOOL = 'tools/tree-tm'
	def __init__( self, runID ):
		self.runID = runID
		self.PATH = '{}/{}'.format( self.ROOT, self.runID )
	
	HYPER_PARAMS = """DEFAULT_ 0.01
NL_ 0.01
ML_ 100
CL_ 0.00000000001
"""
	GENERATE_VOCAB_COMMANDS = """java -cp {tool}/class:{tool}/lib/* cc.mallet.topics.tui.GenerateVocab \\
	--input {runPath}/{runID}.mallet \\
	--vocab {runPath}/{runID}.voc"""

	INIT_BASH_SCRIPT = """#!/bin/bash

echo ">> Generating correlations..."
java -cp {tool}/class:{tool}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {runPath}/{runID}.voc \\
	--constraint {entryPath}/constraint.all \\
	--tree {entryPath}/{runID}.wn \\
	--merge-constraints false

echo ">> Start training a topic model..."
java -cp {tool}/class:{tool}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {runPath}/{runID}.mallet \\
	--output-interval {endIter} \\
	--output-dir {entryPath}/model \\
	--vocab {runPath}/{runID}.voc \\
	--tree {entryPath}/{runID}.wn \\
	--tree-hyperparameters {runPath}/tree_hyperparams \\
	--inferencer-filename {entryPath}/inferencer \\
	--alpha 0.5 \\
	--num-topics {numTopics} \\
	--num-iterations {endIter} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume false \\
	--constraint {entryPath}/constraint.all \\
	--remove-words {entryPath}/removed \\
	--keep {entryPath}/important.keep
"""
	RESUME_BASH_SCRIPT = """#!/bin/bash

echo ">> Generating correlations..."
java -cp {tool}/class:{tool}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {runPath}/{runID}.voc \\
	--constraint {entryPath}/constraint.all \\
	--tree {entryPath}/{runID}.wn \\
	--merge-constraints false

echo ">> Resume training a topic model..."
java -cp {tool}/class:{tool}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {runPath}/{runID}.mallet \\
	--output-interval {endIter} \\
	--output-dir {entryPath}/model \\
	--vocab {runPath}/{runID}.voc \\
	--tree {entryPath}/{runID}.wn \\
	--tree-hyperparameters {runPath}/tree_hyperparams \\
	--inferencer-filename {entryPath}/inferencer \\
	--alpha 0.5 \\
	--num-topics {numTopics} \\
	--num-iterations {endIter} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume true \\
	--resume-dir {entryParentPath}/model \\
	--constraint {entryPath}/constraint.all \\
	--remove-words {entryPath}/removed \\
	--keep {entryPath}/important.keep
"""
	def _CreateHyperParamsFile_( self ):
		filename = '{}/tree_hyperparams'.format( self.PATH )
		with open( filename, 'w' ) as f:
			f.write( self.HYPER_PARAMS )

	def _CreateVocabFile_( self ):
		script = self.GENERATE_VOCAB_COMMANDS.format(
			tool = self.TOOL,
			runID = self.runID,
			runPath = '{}'.format( self.PATH )
		)
		os.system( script )
	
	def _ReadVocabFile_( self ):
		filename = '{}/{}.voc'.format( self.PATH, self.runID )
		with open( filename ) as f:
			vocab = [ line.split( '\t' )[1] for line in f.read().splitlines() ]
		vocab.sort()
		return vocab

	def _ReadStatesFile_( self, entryID ):
		filename = '{}/entry-{:04d}/states.json'.format( self.PATH, entryID )
		try:
			with open( filename ) as f:
				return json.load( f, encoding = 'utf-8' )
		except IOError:
			return None

	def _WriteStatesFile_( self, entryID, states ):
		filename = '{}/entry-{:04d}/states.json'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
			json.dump( states, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def _ReadRunIndexFile_( self ):
		index_filename = '{}/index.json'.format( self.PATH )
		try:
			with open( index_filename ) as f:
				data = json.load( f, encoding = 'utf-8' )
		except IOError:
			data = None
		return data
	
	def _WriteRunIndexFile_( self, data ):
		index_filename = '{}/index.json'.format( self.PATH )
		with open( index_filename, 'w' ) as f:
			json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )
	
	def _CreateEntryFolder_( self, entryID ):
		dirname = '{}/entry-{:04d}'.format( self.PATH, entryID )
		if not os.path.exists( dirname ):
			os.makedirs( dirname )
	
	def _WriteContraintAllFile_( self, runIndex, entryID ):
		numTopics = runIndex['numTopics']
		states = self._ReadStatesFile_( entryID )
		terms = states['rowLabels']
		promotionLists = []  # lists of entries {rowIndex, columnIndex} grouped by topics, representing terms-topics to be kept together
		demotionLists = []   # lists of entries {rowIndex, columnIndex} grouped by topics, representing terms-topics to be separated
		if 'entryProDemotions' in states:
			entryProDemotions = states['entryProDemotions']
			print entryProDemotions
			allPromotions = []
			allDemotions = []
			for key, value in entryProDemotions.iteritems():
				s, t = key.split( ":" )
				s = int(s)
				t = int(t)
				if value is True:
					allPromotions.append( { 'rowIndex' : s, 'columnIndex' : t } )
				else:
					allDemotions.append( { 'rowIndex' : s, 'columnIndex' : t } )
			print allPromotions
			promotionLists = [ [ d for d in allPromotions if d['columnIndex'] == t ] for t in range(numTopics) ]
			demotionLists = [ [ d for d in allDemotions if d['columnIndex'] == t ] for t in range(numTopics) ]
			print promotionLists
		filename = '{}/entry-{:04d}/constraint.all'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
			for promotions in promotionLists:
				if len(promotions) > 0:
					action = 'MERGE_'
					arguments = [ terms[promotion['rowIndex']] for promotion in promotions ]
					f.write( u'{}\t{}\n'.format( action, '\t'.join( arguments ) ).encode( 'utf-8' ) )
			for demotions in demotionLists:
				if len(demotions) > 0:
					action = 'SPLIT_'
					arguments = [ terms[demotion['rowIndex']] for demotion in demotions ]
					f.write( u'{}\t{}\n'.format( action, '\t'.join( arguments ) ).encode( 'utf-8' ) )
	
	def _WriteRemoveAllFile_( self, runIndex, entryID ):
		states = self._ReadStatesFile_( entryID )
		terms = states['rowLabels']
		removals = []	# a list of rows, to be included/excluded
		if 'rowInExclusions' in states:
			pass
		
		filename = '{}/entry-{:04d}/removed.all'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
			for removal in removals:
				f.write( u'{}\n'.format( terms[removal] ).encode( 'utf-8' ) )
	
	def _WriteRemovedNewFile_( self, runIndex, entryID ):
		entry = runIndex['entries'][entryID]
		states = self._ReadStatesFile_( entryID )
		terms = states['rowLabels']
		removals = []	# a list of rows, to be included/excluded since the last iteration
		if 'rowInExclusions' in states:
#			parentStates = runIndex['entries'][entry['entryParentID']]['states']
			pass
		
		filename = '{}/entry-{:04d}/removed.new'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
 			for removal in removals:
				f.write( u'{}\n'.format( terms[removal] ).encode( 'utf-8' ) )
	
	def _WriteImportantKeepFile_( self, runIndex, entryID ):
		states = self._ReadStatesFile_( entryID )
		terms = states['rowLabels']
		promotions = []  # a list of entries {rowIndex, columnIndex}, representing terms-topics to be kept together
		if 'entryProDemotions' in states:
			entryProDemotions = states['entryProDemotions']
			for key, value in entryProDemotions.iteritems():
				s, t = key.split( ":" )
				s = int(s)
				t = int(t)
				if value is True:
					promotions.append( { 'rowIndex' : s, 'columnIndex' : t } )
		
		filename = '{}/entry-{:04d}/important.keep'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
			for promotion in promotions:
				f.write( u'{} {}\n'.format( terms[promotion['rowIndex']], promotion['columnIndex'] ) )
	
	def _WriteInitBashScript_( self, runIndex, entryID ):
		script = self.INIT_BASH_SCRIPT.format(
			tool = self.TOOL,
			runID = self.runID,
			runPath = '{}'.format( self.PATH ),
			entryID = entryID,
			entryPath = '{}/entry-{:04d}'.format( self.PATH, entryID ),
			endIter = runIndex['entries'][entryID]['endIter'],
			numTopics = runIndex['numTopics']
		)
		filename = '{}/entry-{:04d}/execute.sh'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
			f.write( script )
		os.chmod( filename, 0755 )
	
	def _WriteResumeBashScript_( self, runIndex, entryID ):
		script = self.RESUME_BASH_SCRIPT.format(
			tool = self.TOOL,
			runID = self.runID,
			runPath = '{}'.format( self.PATH ),
			entryID = entryID,
			entryPath = '{}/entry-{:04d}'.format( self.PATH, entryID ),
			endIter = runIndex['entries'][entryID]['endIter'],
			numTopics = runIndex['numTopics'],
			entryParentPath = '{}/entry-{:04d}'.format( self.PATH, runIndex['entries'][entryID]['entryParentID'] )
		)
		filename = '{}/entry-{:04d}/execute.sh'.format( self.PATH, entryID )
		with open( filename, 'w' ) as f:
			f.write( script )
		os.chmod( filename, 0755 )
	
	def _InitRunIndex_( self, numTopics ):
		self._CreateHyperParamsFile_()
		self._CreateVocabFile_()
		terms = self._ReadVocabFile_()
		numTerms = len(terms)
		runIndex = {
			'runID' : self.runID,
			'nextEntryID' : 0,
			'numTopics' : numTopics,
			'numTerms' : numTerms,
			'entries' : []
		}
		return runIndex
	
	def _AppendRunIndex_( self, runIndex, entryParentID, numIters, entryDescription ):
		entryID = runIndex['nextEntryID']
		
		if entryParentID is None:
			startIter = 0
			endIter = numIters
		else:
			entryParent = runIndex['entries'][entryParentID]
			startIter = entryParent['endIter']
			endIter = startIter + numIters
		
		entry = {
			'runID' : self.runID,
			'entryID' : entryID,
			'entryDescription' : entryDescription,
			'entryParentID' : entryParentID,
			'startIter' : startIter,
			'endIter' : endIter,
			'numIters' : numIters
		}
		runIndex['nextEntryID'] = entryID + 1
		runIndex['entries'].append( entry )
		return runIndex
	
	def _ValidateStates_( self, runIndex, states ):
		if 'modelType' not in states:
			states['modelType'] = 'TreeTM'
		if 'rowLabels' not in states:
			terms = self._ReadVocabFile_()
			states['rowLabels'] = terms
		if 'columnLabels' not in states:
			numTopics = runIndex['numTopics']
			states['columnLabels'] = [ 'Topic {}'.format(d+1) for d in range(numTopics) ]
		return states

	def _ExecuteBashScript_( self, entryID ):
		filename = "data/{}/entry-{:04d}/execute.sh".format( self.runID, entryID )
		os.system( os.path.abspath(filename) )
	
	def InitEntry( self, numTopics = 10, numIters = 1000, entryDescription = "Initial Model", states = None ):
		runIndex = self._InitRunIndex_( numTopics )
		entryID = runIndex['nextEntryID']

		if states is None:
			states = {}
		states = self._ValidateStates_( runIndex, states )

		runIndex = self._AppendRunIndex_( runIndex, None, numIters, entryDescription )

		self._CreateEntryFolder_( entryID )
		self._WriteStatesFile_( entryID, states )
		self._WriteContraintAllFile_( runIndex, entryID )
		self._WriteRemoveAllFile_( runIndex, entryID )
		self._WriteRemovedNewFile_( runIndex, entryID )
		self._WriteImportantKeepFile_( runIndex, entryID )
		self._WriteInitBashScript_( runIndex, entryID )
		self._WriteRunIndexFile_( runIndex )
		self._ExecuteBashScript_( entryID )
		return entryID
	
	def UpdateEntry( self, entryParentID, numIters = 50, entryDescription = "Updated Model", states = None ):
		runIndex = self._ReadRunIndexFile_()
		if runIndex is None:
			return None
		if not ( 0 <= entryParentID < runIndex['nextEntryID'] ):
			return None
		entryID = runIndex['nextEntryID']

		if states is None:
			states = self._ReadStatesFile_( entryID )
		if states is None:
			states = self._ReadStatesFile_( entryParentID )
		states = self._ValidateStates_( runIndex, states )

		runIndex = self._AppendRunIndex_( runIndex, entryParentID, numIters, entryDescription )

		self._CreateEntryFolder_( entryID )
		self._WriteStatesFile_( entryID, states )
		self._WriteContraintAllFile_( runIndex, entryID )
		self._WriteRemoveAllFile_( runIndex, entryID )
		self._WriteRemovedNewFile_( runIndex, entryID )
		self._WriteImportantKeepFile_( runIndex, entryID )
		self._WriteResumeBashScript_( runIndex, entryID )
		self._WriteRunIndexFile_( runIndex )
		self._ExecuteBashScript_( entryID )
		return entryID
