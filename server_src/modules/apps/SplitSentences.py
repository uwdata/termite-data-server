#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builtins import object
import logging
import subprocess

class SplitSentences(object):

	SENTENCE_SPLITTER = 'utils/corenlp/SentenceSplitter.jar'

	def __init__( self, inputCorpusFilename, outputSentenceFilename ):
		self.logger = logging.getLogger('termite')
		command = [ "java", "-jar", "-Xmx2g", SplitSentences.SENTENCE_SPLITTER, inputCorpusFilename, outputSentenceFilename ]
		self.Shell( command )
		
	def Shell( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )
