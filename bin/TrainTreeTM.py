#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import logging
import json

MALLET_ROOT = 'tools/mallet-2.0.7'
TREETM_ROOT = 'tree_tm'

class TrainTreeTM:
	def __init__( self, corpus_path, model_path, mallet_root, treetm_root, parent_run, logging_level ):
		self.corpus_path = corpus_path
		self.model_path = model_path
		self.mallet_root = mallet_root
		self.treetm_root = treetm_root
		
		self.CreateModelFolder()
		latest_run = self.GetLatestRun()
		if not os.path.exists( self.model_path ):
			self.prev_run = -1
		else:
			if os.path.exists( self.GetRunPath( parent_run ) ):
				self.prev_run = parent_run
			else:
				self.prev_run = latest_run
		self.this_run = latest_run + 1
		self.this_run_path = self.GetRunPath( self.this_run )
		self.prev_run_path = self.GetRunPath( self.prev_run )
		
		self.logger = logging.getLogger( 'ImportMallet' )
		self.logger.setLevel( logging_level )
		handler = logging.StreamHandler( sys.stderr )
		handler.setLevel( logging_level )
		self.logger.addHandler( handler )
	
	HYPER_PARAMS = """DEFAULT_ 0.01
NL_ 0.01
ML_ 100
CL_ 0.00000000001
"""

	IMPORT_FROM_FILE_SCRIPT = """
echo "# Importing file into Mallet: [{CORPUS_PATH}] --> [{MODEL_PATH}/corpus.mallet]"
{MALLET_ROOT}/bin/mallet import-file \\
	--input {CORPUS_PATH} \\
	--output {MODEL_PATH}/corpus.mallet \\
	--remove-stopwords \\
	--token-regex "\p{{Alpha}}{{3,}}" \\
	--keep-sequence
echo
"""

	IMPORT_FROM_FOLDER_SCRIPT = """
echo "# Importing file into Mallet: [{CORPUS_PATH}] --> [{MODEL_PATH}/corpus.mallet]"
{MALLET_ROOT}/bin/mallet import-dir \\
	--input {CORPUS_PATH} \\
	--output {MODEL_PATH}/corpus.mallet \\
	--remove-stopwords \\
	--token-regex "\p{{Alpha}}{{3,}}" \\
	--keep-sequence
echo
"""

	GENERATE_VOCAB_SCRIPT = """
echo "# Generating vocab file: [{MODEL_PATH}/corpus.mallet] -> [{MODEL_PATH}/corpus.voc]"
java -cp {TREETM_ROOT}/class:{TREETM_ROOT}/lib/* cc.mallet.topics.tui.GenerateVocab \\
	--input {MODEL_PATH}/corpus.mallet \\
	--vocab {MODEL_PATH}/corpus.voc
echo
"""

	INIT_TRAINING_SCRIPT = """
echo "# Generating correlations..."
java -Xmx6g -cp {TREETM_ROOT}/class:{TREETM_ROOT}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {MODEL_PATH}/corpus.voc \\
	--constraint {THIS_RUN_PATH}/constraint.all \\
	--tree {THIS_RUN_PATH}/corpus.wn \\
	--merge-constraints false
echo

echo "# Start training a topic model..."
java -Xmx6g -cp {TREETM_ROOT}/class:{TREETM_ROOT}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {MODEL_PATH}/corpus.mallet \\
	--output-interval 25 \\
	--output-dir {THIS_RUN_PATH}/model \\
	--vocab {MODEL_PATH}/corpus.voc \\
	--tree {THIS_RUN_PATH}/corpus.wn \\
	--tree-hyperparameters {MODEL_PATH}/tree_hyperparams.txt \\
	--inferencer-filename {THIS_RUN_PATH}/inferencer \\
	--alpha 0.5 \\
	--num-topics {NUM_TOPICS} \\
	--num-iterations {END_ITERS} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume false \\
	--constraint {THIS_RUN_PATH}/constraint.all \\
	--remove-words {THIS_RUN_PATH}/removed \\
	--keep {THIS_RUN_PATH}/important.keep
echo
"""
	RESUME_TRAINING_SCRIPT = """
echo "# Generating correlations..."
java -Xmx6g -cp {TREETM_ROOT}/class:{TREETM_ROOT}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {MODEL_PATH}/corpus.voc \\
	--constraint {THIS_RUN_PATH}/constraint.all \\
	--tree {THIS_RUN_PATH}/corpus.wn \\
	--merge-constraints false
echo

echo "# Resume training a topic model..."
java -Xmx6g -cp {TREETM_ROOT}/class:{TREETM_ROOT}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {MODEL_PATH}/corpus.mallet \\
	--output-interval 25 \\
	--output-dir {THIS_RUN_PATH}/model \\
	--vocab {MODEL_PATH}/corpus.voc \\
	--tree {THIS_RUN_PATH}/corpus.wn \\
	--tree-hyperparameters {MODEL_PATH}/tree_hyperparams.txt \\
	--inferencer-filename {THIS_RUN_PATH}/inferencer \\
	--alpha 0.5 \\
	--num-topics {NUM_TOPICS} \\
	--num-iterations {END_ITERS} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume true \\
	--resume-dir {PREV_RUN_PATH}/model \\
	--constraint {THIS_RUN_PATH}/constraint.all \\
	--remove-words {THIS_RUN_PATH}/removed \\
	--keep {THIS_RUN_PATH}/important.keep
echo
"""

	def GetRunPath( self, iter ):
		return '{}/{:06d}'.format( self.model_path, iter )
	
	def GetLatestRun( self ):
		latest_run = -1
		for filename in os.listdir( self.model_path ):
			path = '{}/{}'.format( self.model_path, filename )
			if os.path.isdir( path ):
				n = int( filename )
				latest_run = max( latest_run, n )
		return latest_run

	def CreateHyperParamsFile( self ):
		filename = '{}/tree_hyperparams.txt'.format( self.model_path )
		with open( filename, 'w' ) as f:
			f.write( self.HYPER_PARAMS )

	def CreateModelFolder( self ):
		if not os.path.exists( self.model_path ):
			os.makedirs( self.model_path )

	def CreateRunFolder( self ):
		if not os.path.exists( self.this_run_path ):
			os.makedirs( self.this_run_path )

	def ImportFromFileScript( self ):
		script = self.IMPORT_FROM_FILE_SCRIPT.format(
			CORPUS_PATH = self.corpus_path,
			MODEL_PATH = self.model_path,
			MALLET_ROOT = self.mallet_root
		)
		return script

	def ImportFromFolderScript( self ):
		script = self.IMPORT_FROM_FOLDER_SCRIPT.format(
			CORPUS_PATH = self.corpus_path,
			MODEL_PATH = self.model_path,
			MALLET_ROOT = self.mallet_root
		)
		return script

	def GenerateVocabScript( self ):
		script = self.GENERATE_VOCAB_SCRIPT.format(
			TREETM_ROOT = self.treetm_root,
			MODEL_PATH = self.model_path
		)
		return script

	def InitTrainingScript( self, runIndex ):
		script = self.INIT_TRAINING_SCRIPT.format(
			TREETM_ROOT = self.treetm_root,
			MODEL_PATH = self.model_path,
			THIS_RUN_PATH = self.this_run_path,
			END_ITERS = runIndex['numIters'],
			NUM_TOPICS = runIndex['numTopics']
		)
		return script
	
	def ResumeTrainingScript( self, runIndex ):
		script = self.RESUME_TRAINING_SCRIPT.format(
			TREETM_ROOT = self.treetm_root,
			MODEL_PATH = self.model_path,
			THIS_RUN_PATH = self.this_run_path,
			PREV_RUN_PATH = self.prev_run_path,
			END_ITERS = runIndex['numIters'],
			NUM_TOPICS = runIndex['numTopics']
		)
		return script

	def ReadRunIndexFile( self ):
		index_filename = '{}/index.json'.format( self.model_path )
		try:
			with open( index_filename ) as f:
				data = json.load( f, encoding = 'utf-8' )
		except IOError:
			data = None
		return data

	def WriteRunIndexFile( self, data ):
		index_filename = '{}/index.json'.format( self.model_path )
		with open( index_filename, 'w' ) as f:
			json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def ReadPrevStatesFile( self ):
		filename = '{}/states.json'.format( self.prev_run_path )
		try:
			with open( filename ) as f:
				return json.load( f, encoding = 'utf-8' )
		except IOError:
			return {}
	
	def ReadUpdatedStatesFile( self ):
		filename = '{}/updates.json'.format( self.prev_run_path )
		try:
			with open( filename ) as f:
				return json.load( f, encoding = 'utf-8' )
		except IOError:
			return {}

	def WriteStatesFile( self, thisStates ):
		filename = '{}/states.json'.format( self.this_run_path )
		with open( filename, 'w' ) as f:
			json.dump( thisStates, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def WriteContraintAllFile( self, thisStates ):
		promotionLists = []
		demotionLists = []
		if 'promotions' in thisStates:
			prmotionLists = thisStates['promotions']
		if 'demotions' in thisStates:
			demotionLists = thisStates['demotions']
		filename = '{}/constraint.all'.format( self.this_run_path )
		with open( filename, 'w' ) as f:
			for topic in promotionLists:
				promotions = promotionLists[topic]
				if len(promotions) > 0:
					action = 'MERGE_'
					terms = [ term for term in promotions ]
					f.write( u'{}\t{}\n'.format( action, '\t'.join( terms ) ).encode( 'utf-8' ) )
			for topic in demotionLists:
				demotions = demotionLists[topic]
				if len(demotions) > 0:
					action = 'SPLIT_'
					terms = [ term for term in demotions ]
					f.write( u'{}\t{}\n'.format( action, '\t'.join( terms ) ).encode( 'utf-8' ) )
	
	def WriteRemoveAllFile( self, thisStates ):
		removedTerms = []
		if 'removedTerms' in thisStates:
			removedTerms = thisStates['removedTerms']
		filename = '{}/removed.all'.format( self.this_run_path )
		with open( filename, 'w' ) as f:
			for term in removedTerms:
				f.write( u'{}\n'.format( term ).encode( 'utf-8' ) )
	
	def WriteRemovedNewFile( self, thisStates, prevStates ):
		allRemovedTerms = []
		if 'removedTerms' in thisStates:
			allRemovedTerms = thisStates['removedTerms']
		prevRemovedTerms = []
		if 'removedTerms' in prevStates:
			prevRemovedTerms = prevStates['removedTerms']
		allRemovedTerms = frozenset( allRemovedTerms )
		prevRemovedTerms = frozenset( prevRemovedTerms )
		removedTerms = allRemovedTerms.difference( prevRemovedTerms )
		filename = '{}/removed.new'.format( self.this_run_path )
		with open( filename, 'w' ) as f:
 			for term in removedTerms:
				f.write( u'{}\n'.format( term ).encode( 'utf-8' ) )
	
	def WriteImportantKeepFile( self, thisStates ):
		filename = '{}/important.keep'.format( self.this_run_path )
		with open( filename, 'w' ) as f:
			pass
#			for promotion in promotions:
#				f.write( u'{} {}\n'.format( terms[promotion['rowIndex']], promotion['columnIndex'] ) )
		
	def WriteBashScript( self, script ):
		filename = "{}/execute.sh".format( self.this_run_path )
		with open( filename, 'w' ) as f:
			f.write( script )
		os.chmod( filename, 0755 )
			
	def ExecuteBashScript( self ):
		filename = "{}/execute.sh".format( self.this_run_path )
		os.system( os.path.abspath(filename) )
	
	def InitRunIndex( self, numTopics ):
		runIndex = {
			'numTopics' : numTopics,
			'numIters' : 0,
			'entries' : {}
		}
		return runIndex

	def UpdateRunIndex( self, runIndex, numIters ):
		if self.prev_run < 0:
			startIter = 0
			endIter = numIters
		else:
			startIter = runIndex['entries'][ str(self.prev_run) ]['endIter']
			endIter = startIter + numIters
		entry = {
			'runID' : self.this_run,
			'prevRunID' : self.prev_run,
			'startIter' : startIter,
			'endIter' : endIter,
			'numIters' : numIters
		}
		runIndex['numIters'] = endIter
		runIndex['entries'][ str(self.this_run) ] = entry
		return runIndex
	
	def Execute( self, numTopics, numIters, isImportFile ):
		self.logger.info( '--------------------------------------------------------------------------------' )
		self.logger.info( 'Training a tree topic model...'                                                   )
		self.logger.info( '      corpus = %s', self.corpus_path                                              )
		self.logger.info( '       model = %s', self.model_path                                               )
		self.logger.info( '    prev-run = %d', self.prev_run                                                 )
		self.logger.info( '    this-run = %d', self.this_run                                                 )
		self.logger.info( '      mallet = %s', self.mallet_root                                              )
		self.logger.info( '     tree_tm = %s', self.treetm_root                                              )
		self.logger.info( '--------------------------------------------------------------------------------' )

		if self.prev_run < 0:
			runIndex = self.InitRunIndex( numTopics )
			runIndex = self.UpdateRunIndex( runIndex, numIters )

			prevStates = {}
			thisStates = {}
			self.CreateRunFolder()
			self.WriteStatesFile( thisStates )
			self.WriteContraintAllFile( thisStates )
			self.WriteRemoveAllFile( thisStates )
			self.WriteRemovedNewFile( thisStates, prevStates )
			self.WriteImportantKeepFile( thisStates )
			
			self.CreateHyperParamsFile()
			script = [ "#/bin/bash" ]
			if isImportFile:
				script.append( self.ImportFromFileScript() )
			else:
				script.append( self.ImportFromFolderScript() )
			script.append( self.GenerateVocabScript() )
			script.append( self.InitTrainingScript( runIndex ) )

		else:
			runIndex = self.ReadRunIndexFile()
			runIndex = self.UpdateRunIndex( runIndex, numIters )
			
			prevStates = self.ReadPrevStatesFile()
			thisStates = self.ReadUpdatedStatesFile()
			self.CreateRunFolder()
			self.WriteStatesFile( thisStates )
			self.WriteContraintAllFile( thisStates )
			self.WriteRemoveAllFile( thisStates )
			self.WriteRemovedNewFile( thisStates, prevStates )
			self.WriteImportantKeepFile( thisStates )
		
			script = [ "#/bin/bash" ]
			script.append( self.ResumeTrainingScript( runIndex ) )
		
		script = '\n'.join( script )
		self.WriteRunIndexFile( runIndex )
		self.WriteBashScript( script )
		self.ExecuteBashScript()

def main():
	parser = argparse.ArgumentParser( description = 'Train a tree topic model'                               )
	parser.add_argument( 'corpus_path'  , type = str , help = 'Input text corpus'                            )
	parser.add_argument( 'model_path'   , type = str , help = 'Output model'                                 )
	parser.add_argument( '--mallet_root', type = str , help = 'Path to MALLET'       , default = MALLET_ROOT )
	parser.add_argument( '--treetm_root', type = str , help = 'Path to TreeTM'       , default = TREETM_ROOT )
	parser.add_argument( '--parent'     , type = int , help = 'Parent run'           , default = -1          )
	parser.add_argument( '--topics'     , type = int , help = 'Number of topics'     , default = 20          )
	parser.add_argument( '--iters'      , type = int , help = 'Number of iterations' , default = 50          )
	parser.add_argument( '--is_file'    , help = 'Import as file (instead of folder)', action = 'store_const', const = True, default = False )
	parser.add_argument( '--logging'    , type = int , help = 'Override default logging level', default = 20 )
	args = parser.parse_args()

	TrainTreeTM(
		corpus_path = args.corpus_path,
		model_path = args.model_path, 
		mallet_root = args.mallet_root,
		treetm_root = args.treetm_root,
		parent_run = args.parent,
		logging_level = args.logging
	).Execute(
		numTopics = args.topics,
		numIters = args.iters,
		isImportFile = args.is_file
	)

if __name__ == '__main__':
	main()
