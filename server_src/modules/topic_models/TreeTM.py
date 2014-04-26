#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import shutil
import subprocess

class RefineLDA(object):
	"""
	modelPath = Folder for storing all output files
	numIters = Other parameters
	mustLinkConstraints = a list of lists of words
	cannotLinkConstraints = a list of lists of words
	keepTerms = a dict where the keys are topic indexes and the values are a list of words
	removeTerms = a list of words
	"""
	def __init__( self, modelPath, numIters = 1000, prevEntry = None,
			mustLinks = None, cannotLinks = None, keepTerms = None, removeTerms = None,
			MALLET_PATH = 'tools/mallet' ):
		with TreeTM( modelsPath = modelPath, resume = True, finalIter = numIters, prevEntryID = prevEntry ) as treeTM:
			treeTM.ResumeTraining()
			if mustLinks is not None:
				treeTM.SetMustLinkConstraints( mustLinks )
			if cannotLinks is not None:
				treeTM.SetCannotLinkConstraints( cannotLinks )
			if keepTerms is not None:
				treeTM.SetKeepTerms( keepTerms )
			if removeTerms is not None:
				treeTM.SetRemoveTerms( removeTerms )
			treeTM.WriteFiles()
			treeTM.Execute()
	
class BuildLDA(object):
	"""
	corpusPath = A single tab-delimited file containing the corpus (one document per line, two columns containing docID and docContent, without headers)
	modelPath = Folder for storing all output files
	tokenRegex, numTopics, numIters = Other parameters
	mustLinkConstraints = a list of lists of words
	cannotLinkConstraints = a list of lists of words
	keepTerms = a dict where the keys are topic indexes and the values are a list of words
	removeTerms = a list of words
	"""
	def __init__( self, corpusPath, modelPath, tokenRegex = r'\w{3,}', numTopics = 20, numIters = 1000,
			mustLinks = None, cannotLinks = None, keepTerms = None, removeTerms = None,
			MALLET_PATH = 'tools/mallet' ):
		with TreeTM( corpusPath = corpusPath, modelsPath = modelPath, resume = False, tokenRegex = tokenRegex, numTopics = numTopics, finalIter = numIters ) as treeTM:
			treeTM.StartTraining()
			if mustLinks is not None:
				treeTM.SetMustLinkConstraints( mustLinks )
			if cannotLinks is not None:
				treeTM.SetCannotLinkConstraints( cannotLinks )
			if keepTerms is not None:
				treeTM.SetKeepTerms( keepTerms )
			if removeTerms is not None:
				treeTM.SetRemoveTerms( removeTerms )
			treeTM.WriteFiles()
			treeTM.Execute()

HYPER_PARAMS = u"""DEFAULT_ 0.01
NL_ 0.01
ML_ 100
CL_ 0.00000000001
"""

GENERATE_VOCAB_COMMAND = [
	"java", "-Xmx8g",
	"-cp", "{TREETM_PATH}/class:{TREETM_PATH}/lib/*", "cc.mallet.topics.tui.GenerateVocab",
	"--input", "{filenameMallet}",
	"--vocab", "{filenameVocab}"
]

INIT_BASH_SCRIPT = u"""#!/bin/bash

echo ">> Generate correlations..."
java -Xmx8g -cp {TREETM_PATH}/class:{TREETM_PATH}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {filenameVocab} \\
	--constraint {filenameConstraints} \\
	--tree {filenameWN} \\
	--merge-constraints false

echo ">> Start training a topic model..."
java -Xmx8g -cp {TREETM_PATH}/class:{TREETM_PATH}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {filenameMallet} \\
	--output-interval {finalIter} \\
	--output-dir {filenameNextModel} \\
	--vocab {filenameVocab} \\
	--tree {filenameWN} \\
	--tree-hyperparameters {filenameHyperparams} \\
	--inferencer-filename {filenameInferencer} \\
	--alpha 0.5 \\
	--num-topics {numTopics} \\
	--num-iterations {finalIter} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume false \\
	--constraint {filenameConstraints} \\
	--remove-words {filenameRemoveTermsPrefix} \\
	--keep {filenameKeepTerms}
"""

RESUME_BASH_SCRIPT = u"""#!/bin/bash

echo ">> Generate correlations..."
java -Xmx8g -cp {TREETM_PATH}/class:{TREETM_PATH}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {filenameVocab} \\
	--constraint {filenameConstraints} \\
	--tree {filenameWN} \\
	--merge-constraints false

echo ">> Resume training a topic model..."
java -Xmx8g -cp {TREETM_PATH}/class:{TREETM_PATH}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {filenameMallet} \\
	--output-interval {finalIter} \\
	--output-dir {filenameNextModel} \\
	--vocab {filenameVocab} \\
	--tree {filenameWN} \\
	--tree-hyperparameters {filenameHyperparams} \\
	--inferencer-filename {filenameInferencer} \\
	--alpha 0.5 \\
	--num-topics {numTopics} \\
	--num-iterations {finalIter} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume true \\
	--resume-dir {filenamePrevModel} \\
	--constraint {filenameConstraints} \\
	--remove-words {filenameRemoveTermsPrefix} \\
	--keep {filenameKeepTerms}
"""

class TreeTM(object):
	def __init__( self, corpusPath = None, modelsPath = None, tokenRegex = None, resume = False, prevEntryID = None, numTopics = None, finalIter = None, MALLET_PATH = 'tools/mallet', TREETM_PATH = 'tools/treetm' ):
		self.logger = logging.getLogger('termite')
		self.TREETM_PATH = TREETM_PATH
		self.MALLET_PATH = MALLET_PATH
		
		if resume:
			assert modelsPath is not None
			assert finalIter is not None
		else:
			assert corpusPath is not None
			assert modelsPath is not None
			assert tokenRegex is not None
			assert finalIter is not None
			assert numTopics is not None

		self.corpusPath = corpusPath
		self.modelsPath = modelsPath
		self.corpusInMallet = '{}/corpus.mallet'.format( self.modelsPath )
		self.filenameIndex       = '{modelsPath}/index.json'.format( modelsPath = self.modelsPath )
		self.filenameMallet      = '{modelsPath}/corpus.mallet'.format( modelsPath = self.modelsPath )
		self.filenameVocab       = '{modelsPath}/corpus.voc'.format( modelsPath = self.modelsPath )
		self.filenameHyperparams = '{modelsPath}/tree_hyperparams'.format( modelsPath = self.modelsPath )

		if resume:
			completedEntryID, nextEntryID, numTopics = self.ReadRunIndexFile()
			if prevEntryID is None:
				self.prevEntryID = completedEntryID
			else:
				self.prevEntryID = prevEntryID
			self.nextEntryID = nextEntryID
			self.numTopics = numTopics
			self.logger.info( 'Training an existing interactive topic model: [%s][entry-%06d] --> [%s][entry-%06d]', self.modelsPath, self.prevEntryID, self.modelsPath, self.nextEntryID )
		else:
			nextEntryID, numTopics = self.CreateRunIndexFile( numTopics )
			self.prevEntryID = -1
			self.nextEntryID = nextEntryID
			self.numTopics = numTopics
			self.tokenRegex = tokenRegex
			self.logger.info( 'Training a new interactive topic model: [%s] --> [%s][entry-%06d]', self.corpusInMallet, self.modelsPath, self.nextEntryID )

		self.resume = resume
		self.finalIter = finalIter
		self.prevEntryPath = '{modelsPath}/entry-{prevEntryID:06d}'.format( modelsPath = self.modelsPath, prevEntryID = self.prevEntryID )
		self.nextEntryPath = '{modelsPath}/entry-{nextEntryID:06d}'.format( modelsPath = self.modelsPath, nextEntryID = self.nextEntryID )
		self.filenamePrevStates  = '{prevEntryPath}/states.json'.format( prevEntryPath = self.prevEntryPath )
		self.filenamePrevModel   = '{prevEntryPath}/model'.format( prevEntryPath = self.prevEntryPath )
		self.filenameNextStates  = '{nextEntryPath}/states.json'.format( nextEntryPath = self.nextEntryPath )
		self.filenameNextModel   = '{nextEntryPath}/model'.format( nextEntryPath = self.nextEntryPath )
		self.filenameConstraints         = '{nextEntryPath}/constraint.all'.format( nextEntryPath = self.nextEntryPath )
		self.filenameKeepTerms           = '{nextEntryPath}/important.keep'.format( nextEntryPath = self.nextEntryPath )
		self.filenameRemoveTermsPrevious = '{prevEntryPath}/removed.all'.format( prevEntryPath = self.prevEntryPath )
		self.filenameRemoveTermsPrefix   = '{nextEntryPath}/removed'.format( nextEntryPath = self.nextEntryPath )
		self.filenameRemoveTermsNew      = '{nextEntryPath}/removed.new'.format( nextEntryPath = self.nextEntryPath )
		self.filenameRemoveTermsAll      = '{nextEntryPath}/removed.all'.format( nextEntryPath = self.nextEntryPath )
		self.filenameWN                  = '{nextEntryPath}/corpus.wn'.format( nextEntryPath = self.nextEntryPath )
		self.filenameInferencer          = '{nextEntryPath}/inferencer'.format( nextEntryPath = self.nextEntryPath )
		self.filenameExecute = '{nextEntryPath}/execute.sh'.format( nextEntryPath = self.nextEntryPath )
		
		self.hyperParameters = HYPER_PARAMS
		self.generateVocabCommand = [ s.format(
			TREETM_PATH = self.TREETM_PATH, 
			filenameMallet = self.filenameMallet, 
			filenameVocab = self.filenameVocab
		) for s in GENERATE_VOCAB_COMMAND ]
		if resume:
			self.EXECUTE_BASH_SCRIPT = RESUME_BASH_SCRIPT.format(
				TREETM_PATH = self.TREETM_PATH,
				numTopics = self.numTopics,
				finalIter = self.finalIter,
				filenameMallet = self.filenameMallet,
				filenameVocab = self.filenameVocab,
				filenameHyperparams = self.filenameHyperparams,
				filenamePrevModel = self.filenamePrevModel,
				filenameNextModel = self.filenameNextModel,
				filenameConstraints = self.filenameConstraints,
				filenameKeepTerms = self.filenameKeepTerms,
				filenameRemoveTermsPrefix = self.filenameRemoveTermsPrefix,
				filenameWN = self.filenameWN,
				filenameInferencer = self.filenameInferencer
			)
		else:
			self.EXECUTE_BASH_SCRIPT = INIT_BASH_SCRIPT.format(
				TREETM_PATH = self.TREETM_PATH,
				numTopics = self.numTopics,
				finalIter = self.finalIter,
				filenameMallet = self.filenameMallet,
				filenameVocab = self.filenameVocab,
				filenameHyperparams = self.filenameHyperparams,
				filenameNextModel = self.filenameNextModel,
				filenameConstraints = self.filenameConstraints,
				filenameKeepTerms = self.filenameKeepTerms,
				filenameRemoveTermsPrefix = self.filenameRemoveTermsPrefix,
				filenameWN = self.filenameWN,
				filenameInferencer = self.filenameInferencer
			)
		
		self.mustLinkConstraints = []
		self.cannotLinkConstraints = []
		self.keepTerms = {}
		self.removeTermsAll = frozenset()
		self.removeTermsNew = frozenset()

	def __enter__( self ):
		return self

	def __exit__( self, type, value, traceback ):
		pass


################################################################################
# Setters (public methods)
		
	def SetMustLinkConstraints( self, mustLinkConstraints ):
		"""Argument 'mustLinkConstraints' should be a list of lists of words"""
		self.mustLinkConstraints = [ frozenset(constraint) for constraint in mustLinkConstraints ]

	def SetCannotLinkConstraints( self, cannotLinkConstraints ):
		"""Argument 'cannotLinkConstraints' should be a list of lists of words"""
		self.cannotLinkConstraints = [ frozenset(constraint) for constraint in cannotLinkConstraints ]

	def SetKeepTerms( self, keepTerms ):
		"""Argument 'keepTerms' should be a dict where the keys are topic indexes and the values are a list of words"""
		self.keepTerms = {}
		for key, values in keepTerms.iteritems():
			if key in self.keepTerms:
				self.keepTerms[key].update(values)
			else:
				self.keepTerms[key] = set(values)
	
	def SetRemoveTerms( self, removeTerms ):
		"""Argument 'removeTerms' should be a list of words"""
		removeTermsPrevious = self.ReadRemoveTermsFile()
		self.removeTermsAll = frozenset(removeTerms)
		self.removeTermsNew = self.removeTermsAll.difference(removeTermsPrevious)

################################################################################
# File I/O Operations

	def CreateRunIndexFile( self, numTopics ):
		self.CreateModelPath()
		data = {
			"completedEntryID" : -1,
			"nextEntryID" : 1,
			"numTopics" : numTopics
		}
		with open( self.filenameIndex, 'w' ) as f:
			json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		return 0, numTopics
		
	def ReadRunIndexFile( self ):
		with open( self.filenameIndex, 'r' ) as f:
			data = json.load( f, encoding = 'utf-8' )
		completedEntryID = data['completedEntryID']
		nextEntryID = data['nextEntryID']
		numTopics = data['numTopics']
		data["nextEntryID"] += 1
		with open( self.filenameIndex, 'w' ) as f:
			json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )
		return completedEntryID, nextEntryID, numTopics

	def WriteRunIndexFile( self ):
		with open( self.filenameIndex, 'r' ) as f:
			data = json.load( f, encoding = 'utf-8' )
		data["completedEntryID"] = self.nextEntryID
		with open( self.filenameIndex, 'w' ) as f:
			json.dump( data, f, encoding = 'utf-8', indent = 2, sort_keys = True )

	def WriteStatesFile( self ):
		states = {
			'prevEntryID' : self.prevEntryID,
			'numIters' : self.finalIter
		}
		with open( self.filenameNextStates, 'w' ) as f:
			json.dump( states, f, encoding = 'utf-8', indent = 2, sort_keys = True )
	
	def CreateHyperparamsFile( self ):
		with open( self.filenameHyperparams, 'w' ) as f:
			f.write( self.hyperParameters.encode('utf-8') )

	def CreateVocabFile( self ):
		command = self.generateVocabCommand
		self.Shell( command )

	def CreateEntryFolder( self ):
		if not os.path.exists( self.nextEntryPath ):
			os.makedirs( self.nextEntryPath )

	def WriteConstraintsFile( self ):
		lines = []
		for mustLink in self.mustLinkConstraints:
			lines.append( u'MERGE_\t{}'.format( u'\t'.join(term for term in mustLink) ) )
		for cannotLink in self.cannotLinkConstraints:
			lines.append( u'SPLIT_\t{}'.format( u'\t'.join(term for term in cannotLink) ) )
		with open( self.filenameConstraints, 'w' ) as f:
			f.write( u'\n'.join(lines).encode('utf-8') )
	
	def WriteKeepTermsFile( self ):
		lines = []
		for topic, terms in self.keepTerms.iteritems():
			for term in terms:
				lines.append( u'{}\t{}'.format(term, topic) )
		with open( self.filenameKeepTerms, 'w' ) as f:
			f.write( u'\n'.join(lines).encode('utf-8') )

	def ReadRemoveTermsFile( self ):
		with open( self.filenameRemoveTermsPrevious, 'r' ) as f:
			lines = f.read().decode('utf-8').splitlines()
		return frozenset(lines)
		
	def WriteRemoveTermsFiles( self ):
		lines = [ term for term in self.removeTermsAll ]
		with open( self.filenameRemoveTermsAll, 'w' ) as f:
			f.write( u'\n'.join(lines).encode('utf-8') )
		lines = [ term for term in self.removeTermsNew ]
		with open( self.filenameRemoveTermsNew, 'w' ) as f:
			f.write( u'\n'.join(lines).encode('utf-8') )
	
	def WriteExecuteBashScript( self ):
		with open( self.filenameExecute, 'w' ) as f:
			f.write( self.EXECUTE_BASH_SCRIPT.encode('utf-8') )
		os.chmod( self.filenameExecute, 0755 )
		
################################################################################
# Steps in Training a TreeTM

	def CreateModelPath( self ):
		if not os.path.exists( self.modelsPath ):
			self.logger.info( 'Creating model folder: %s', self.modelsPath )
			os.makedirs( self.modelsPath )
	
	def CreateEntryFolder( self ):
		if not os.path.exists( self.nextEntryPath ):
			self.logger.info( 'Creating entry folder: %s', self.nextEntryPath )
			os.makedirs( self.nextEntryPath )

	def CopyEntryFolder( self ):
		if not os.path.exists( self.nextEntryPath ):
			self.logger.info( 'Copying entry folder: %s', self.nextEntryPath )
			shutil.copytree( self.prevEntryPath, self.nextEntryPath )
			with open( self.filenameRemoveTermsNew, 'w' ) as f:
				f.write('')

	def ImportFileOrFolder( self ):
		mallet_executable = '{}/bin/mallet'.format( self.MALLET_PATH )
		if os.path.isdir( self.corpusPath ):
			self.logger.info( 'Importing a folder into MALLET: [%s] --> [%s]', self.corpusPath, self.corpusInMallet )
			command = [ mallet_executable, 'import-dir' ]
		else:
			self.logger.info( 'Importing a file into MALLET: [%s] --> [%s]', self.corpusPath, self.corpusInMallet )
			command = [ mallet_executable, 'import-file' ]
		command += [
			'--input', self.corpusPath,
			'--output', self.corpusInMallet,
			'--remove-stopwords',
			'--token-regex', self.tokenRegex,
			'--keep-sequence'
		]
		self.Shell( command )
	
	def Shell( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			self.logger.debug( p.stdout.readline().rstrip('\n') )
	
	def StartTraining( self ):
		assert not self.resume
		self.CreateEntryFolder()
		self.ImportFileOrFolder()
		self.CreateHyperparamsFile()
		self.CreateVocabFile()
	
	def ResumeTraining( self ):
		assert self.resume
		self.CopyEntryFolder()

	def WriteFiles( self ):
		self.CreateEntryFolder()
		self.WriteStatesFile()
		self.WriteConstraintsFile()
		self.WriteKeepTermsFile()
		self.WriteRemoveTermsFiles()
		self.WriteExecuteBashScript()
	
	def Execute( self ):
		command = [ self.filenameExecute ]
		self.Shell( command )
		self.WriteRunIndexFile()
