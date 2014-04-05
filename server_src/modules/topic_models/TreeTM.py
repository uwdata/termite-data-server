#!/usr/bin/env python

import json
import os
from TreeTM_Templates import HYPER_PARAMS, GENERATE_VOCAB_COMMANDS, INIT_BASH_SCRIPT, RESUME_BASH_SCRIPT

class TreeTM:
	def __init__( self, toolPath = 'tools/treetm', runPath = 'data', resume = False, prevEntryID = None, numTopics = 20, finalIter = 1000 ):
		self.toolPath = toolPath
		self.runPath = runPath
		self.filenameIndex       = '{runPath}/index.json'.format( runPath = self.runPath )
		self.filenameMallet      = '{runPath}/corpus.mallet'.format( runPath = self.runPath )
		self.filenameVocab       = '{runPath}/corpus.voc'.format( runPath = self.runPath )
		self.filenameHyperparams = '{runPath}/tree_hyperparams'.format( runPath = self.runPath )

		if resume:
			lastEntryID, numTopics = self.ReadRunIndexFile()
			if prevEntryID is None:
				self.prevEntryID = lastEntryID
			else:
				self.prevEntryID = prevEntryID
			self.nextEntryID = lastEntryID + 1
		else:
			self.CreateRunIndexFile( numTopics )
			self.prevEntryID = 0
			self.nextEntryID = 0

		self.resume = resume
		self.numTopics = numTopics
		self.finalIter = finalIter
		self.prevEntryPath = '{runPath}/entry-{prevEntryID:06d}'.format( runPath = self.runPath, prevEntryID = self.prevEntryID )
		self.nextEntryPath = '{runPath}/entry-{nextEntryID:06d}'.format( runPath = self.runPath, nextEntryID = self.nextEntryID )
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
		
		self.filenameExecute = os.path.abspath( '{nextEntryPath}/execute.sh'.format( nextEntryPath = self.nextEntryPath ) )
		
		self.HYPER_PARAMS = HYPER_PARAMS
		self.GENERATE_VOCAB_COMMANDS = GENERATE_VOCAB_COMMANDS.format(
			TOOL = self.toolPath, 
			filenameMallet = self.filenameMallet, 
			filenameVocab = self.filenameVocab
		)
		if resume:
			self.EXECUTE_BASH_SCRIPT = RESUME_BASH_SCRIPT.format(
				TOOL = self.toolPath,
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
				TOOL = self.toolPath,
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

################################################################################
# Setters (public methods)
		
	def SetMustLinkConstraints( self, mustLinkConstraints ):
		"""Argument 'mustLinkConstraints' should be a list of lists of words"""
		self.mustLinkConstraints = [ frozenset(constraint) for constaint in mustLinkConstraints ]

	def SetCannotLinkConstraints( self, cannotLinkConstraints ):
		"""Argument 'cannotLinkConstraints' should be a list of lists of words"""
		self.cannotLinkConstraints = [ frozenset(constraint) for constaint in cannotLinkConstraints ]

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
		data = {
			"lastEntryID" : -1,
			"numTopics" : numTopics
		}
		
	def ReadRunIndexFile( self ):
		with open( self.filenameIndex ) as f:
			data = json.load( f, encoding = 'utf-8' )
		lastEntryID = data['lastEntryID']
		numTopics = data['numTopics']
		return lastEntryID, numTopics

	def WriteRunIndexFile( self ):
		with open( self.filenameIndex ) as f:
			data = json.load( f, encoding = 'utf-8' )
		data['lastEntryID'] = self.nextEntryID
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
			f.write( self.HYPER_PARAMS.encode('utf-8') )

	def CreateVocabFile( self ):
		os.system( self.GENERATE_VOCAB_COMMANDS )

	def CreateEntryFolder( self ):
		if not os.path.exists( self.nextEntryPath ):
			os.makedirs( self.nextEntryPath )

	def WriteConstraintsFile( self ):
		lines = []
		for mustLink in self.mustLinkConstraints:
			lines.append( u'MERGE_\t{}'.format(u'\t'.join(term for term in mustLink)) )
		for cannotLink in self.cannotLinkConstraints:
			lines.append( u'SPLIT_\t{}'.format(u'\t'.join(term for term in cannotLink)) )
		with open( self.filenameConstraints, 'w' ) as f:
			f.write( u'\n'.join(lines).encode('utf-8') )
	
	def WriteKeepTermsFile( self ):
		lines = []
		for topic, terms in self.keepTerms:
			for term in terms:
				lines.append( u'{}\t{}'.format(term, topic) )
		with open( self.filenameKeepTerms, 'w' ) as f:
			f.write( u'\n'.join(lines).encode('utf-8') )

	def ReadRemoveTermsFile( self ):
		with open( self.filenamesRemoveTermsPrevious, 'r' ) as f:
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

	def Prepare( self ):
		if not self.resume:
			self.CreateHyperparamsFile()
			self.CreateVocabFile()
		self.CreateEntryFolder()
		self.WriteStatesFile()
		self.WriteConstraintsFile()
		self.WriteKeepTermsFile()
		self.WriteRemoveTermsFiles()
		self.WriteExecuteBashScript()
	
	def Execute( self ):
		os.system( self.filenameExecute )
