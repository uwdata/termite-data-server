#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import subprocess
from CommonLDA import CommonLDA

class STM( CommonLDA ):
	SCRIPT = """# Load an STM model and save its content as Termite Data Server files
# Load required libraries
library(stm)
library(lda)

# Define output filenames
app.path = "{DATA_PATH}"
app.path.TermTopicMatrix = "{DATA_PATH}/term-topic-matrix.txt"
app.path.DocTopicMatrix = "{DATA_PATH}/doc-topic-matrix.txt"
app.path.TermIndex = "{DATA_PATH}/term-index.json"
app.path.DocIndex = "{DATA_PATH}/doc-index.json"
app.path.TopicIndex = "{DATA_PATH}/topic-index.json"

# Load input data
load( file = "{MODEL_FILENAME}" )
model = mod.out

meta = read.delim( file = "{META_FILENAME}", quote = "" )
docIDs = meta["DocID"]

library( jsonlite )

data.DocTopicMatrix = model$theta
data.TermTopicMatrix = exp( t( model$beta$logbeta[[1]] ) )

# Document Index
temp.DocCount <- nrow(model$theta)
temp.DocIDs <- paste( "Document #", 1:temp.DocCount, sep = "" )
temp.DocIndex <- 1:temp.DocCount
temp.DocIndexValues <- cbind( temp.DocIndex, docIDs )
temp.DocIndexHeader <- c( "index", "docID" )
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
rownames( data.DocTopicMatrix ) <- temp.DocIDs
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

	def __init__( self, app_path, model_path, meta_path ):
		self.logger = logging.getLogger('termite')

		self.app_path = app_path
		self.data_path = '{}/data/lda'.format( self.app_path )
		self.model_path = model_path
		self.meta_path = meta_path
		self.script_filename = '{}/import.r'.format( self.data_path )
	
	def Exists( self ):
		return os.path.exists( self.data_path )

	def Execute( self ):
		if not os.path.exists( self.data_path ):
			os.makedirs( self.data_path )
		
		self.logger.info( 'Generating R script: %s', self.script_filename )
		r = STM.SCRIPT.format( DATA_PATH = self.data_path, MODEL_FILENAME = self.model_path, META_FILENAME = self.meta_path )
		with open( self.script_filename, 'w' ) as f:
			f.write( r.encode( 'utf-8' ) )
			
		self.logger.info( 'Executing R script: %s', self.script_filename )
		command = [ 'RScript', self.script_filename ]
		self.RunCommand( command )

		self.ResolveMatrices()
		self.TransposeMatrices()
		self.ComputeTopicCooccurrenceAndCovariance()

	def RunCommand( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )

