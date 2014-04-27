#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import subprocess
from LDAReader import LDAReader

class STMReader(LDAReader):
	"""
	lda_db = a SQLite3 database
	modelPath = a model folder containing an R datafile stm.RData
	"""
	
	PROB_THRESHOLD = 0.0001
	RDATA_FILENAME = 'stm.RData'
	
	SCRIPT = """# Load an STM model and save its content as Termite Data Server files
# Load required libraries
library(stm)
library(lda)

# Define output filenames
app.path = "{DATA_PATH}"
app.path.TermTopicMatrix = "{DATA_PATH}/term-topic-matrix.txt"
app.path.DocTopicMatrix = "{DATA_PATH}/doc-topic-matrix.txt"
app.path.DocIndex = "{DATA_PATH}/doc-index.json"
app.path.TermIndex = "{DATA_PATH}/term-index.json"
app.path.TopicIndex = "{DATA_PATH}/topic-index.json"

# Load input data
load( file = "{MODEL_FILENAME}" )
model = mod.out

library( jsonlite )

data.DocTopicMatrix = model$theta
data.TermTopicMatrix = exp( t( model$beta$logbeta[[1]] ) )

# Document Index
temp.DocCount <- nrow(model$theta)
temp.DocIndex <- 1:temp.DocCount
temp.DocIndexValues <- cbind( temp.DocIndex )
temp.DocIndexHeader <- c( "index" )
colnames( temp.DocIndexValues ) <- temp.DocIndexHeader
data.DocIndexJSON <- toJSON( as.data.frame( temp.DocIndexValues ), pretty = TRUE, digits = 10 )
write( data.DocIndexJSON, file = app.path.DocIndex )

# Term Index
temp.TermCount <- nrow( data.TermTopicMatrix )
temp.TermFreq <- apply( data.TermTopicMatrix, 1, sum )
temp.TermText <- model$vocab
temp.TermIndex <- 1:temp.TermCount
temp.TermIndexValues = cbind( temp.TermIndex, temp.TermFreq, temp.TermText )
temp.TermIndexHeader = c( "index", "freq", "text" )
colnames( temp.TermIndexValues ) <- temp.TermIndexHeader
data.TermIndexJSON <- toJSON( as.data.frame( temp.TermIndexValues ), pretty = TRUE, digits = 10 )
write( data.TermIndexJSON, file = app.path.TermIndex )

# Topic Index
temp.TopicCount <- ncol( data.TermTopicMatrix )
temp.TopicFreq <- apply( data.TermTopicMatrix, 2, sum )
temp.TopicIndex <- 1:temp.TopicCount
temp.TopicIndexValues = cbind( temp.TopicIndex, temp.TopicFreq )
temp.TopicIndexHeader = c( "index", "freq" )
colnames( temp.TopicIndexValues ) <- temp.TopicIndexHeader
data.TopicIndexJSON <- toJSON( as.data.frame( temp.TopicIndexValues ), pretty = TRUE, digits = 10 )
write( data.TopicIndexJSON, file = app.path.TopicIndex )

# Doc-Topic Matrix
# Tab-separated with no headers. Theta (D by K)
rownames( data.DocTopicMatrix ) <- temp.DocIndex
colnames( data.DocTopicMatrix ) <- temp.TopicIndex
data.DocTopicMatrixJSON <- toJSON( data.DocTopicMatrix, pretty = TRUE, digits = 10 )
write( data.DocTopicMatrixJSON, file = app.path.DocTopicMatrix )

# Term-Topic Matrix
# Tab-separated with no headers. Beta (V by K)
rownames( data.TermTopicMatrix ) <- temp.TermText
colnames( data.TermTopicMatrix ) <- temp.TopicIndex
data.TermTopicMatrixJSON <- toJSON( data.TermTopicMatrix, pretty = TRUE, digits = 10 )
write( data.TermTopicMatrixJSON, file = app.path.TermTopicMatrix )

"""

	def __init__( self, lda_db, modelPath, corpus_db ):
		super(STMReader, self).__init__(lda_db)
		self.modelPath = modelPath
		self.modelRData = '{}/{}'.format( self.modelPath, STMReader.RDATA_FILENAME )
		self.modelScript = '{}/import.r'.format( self.modelPath )
		self.ldaTermTopicMatrix = '{}/term-topic-matrix.txt'.format( self.modelPath )
		self.ldaDocTopicMatrix = '{}/doc-topic-matrix.txt'.format( self.modelPath )
		self.ldaDocIndex = '{}/doc-index.json'.format( self.modelPath )
		self.ldaTermIndex = '{}/term-index.json'.format( self.modelPath )
		self.ldaTopicIndex = '{}/topic-index.json'.format( self.modelPath )
		self.corpus = corpus_db.db

	def Execute( self ):
		self.logger.info( 'Reading STM topic model...' )
		self.WriteToDisk()
		self.ReadFromDisk()
		self.logger.info( 'Writing to database...' )
		self.SaveToDB()

	def RunCommand( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )
	
	def WriteToDisk( self ):
		self.logger.debug( '    Writing R script: %s', self.modelScript )
		r = STMReader.SCRIPT.format( DATA_PATH = self.modelPath, MODEL_FILENAME = self.modelRData )
		with open( self.modelScript, 'w' ) as f:
			f.write( r.encode( 'utf-8' ) )
		self.logger.info( 'Executing R script: %s', self.modelScript )
		command = [ 'RScript', self.modelScript ]
		
		self.logger.debug( '    Executing R script: %s', self.modelScript )
		self.RunCommand( command )
	
	def ReadFromDisk( self ):
		self.logger.debug( '    Loading json: %s', self.ldaTermIndex )
		with open( self.ldaTermIndex ) as f:
			data = json.load( f, encoding = 'utf-8' )
		self.termList = [ d['text'] for d in data ]
		self.docList = [ d.doc_id for d in self.corpus().select(self.corpus.corpus.doc_id, orderby=self.corpus.corpus.doc_index) ]

		self.logger.debug( '    Loading matrix: %s', self.ldaTermTopicMatrix )
		with open( self.ldaTermTopicMatrix ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		self.termTopicMatrix = []
		for termIndex, topicFreqs in enumerate(matrix):
			for topicIndex, value in enumerate(topicFreqs):
				if value > STMReader.PROB_THRESHOLD:
					self.termTopicMatrix.append({
						'term_index' : termIndex,
					 	'topic_index' : topicIndex,
						'value' : value,
						'rank' : 0
					})
		self.termTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.termTopicMatrix):
			d['rank'] = index + 1

		self.logger.debug( '    Loading matrix: %s', self.ldaDocTopicMatrix )
		with open( self.ldaDocTopicMatrix ) as f:
			matrix = json.load( f, encoding = 'utf-8' )
		self.docTopicMatrix = []
		for docIndex, topicFreqs in enumerate(matrix):
			for topicIndex, value in enumerate(topicFreqs):
				if value > STMReader.PROB_THRESHOLD:
					self.docTopicMatrix.append({
						'doc_index' : docIndex,
					 	'topic_index' : topicIndex,
						'value' : value,
						'rank' : 0
					})
		self.docTopicMatrix.sort( key = lambda d : -d['value'] )
		for index, d in enumerate(self.docTopicMatrix):
			d['rank'] = index + 1
