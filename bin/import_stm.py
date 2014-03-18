#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import subprocess
from import_abstr import ImportAbstraction

class ImportSTM( ImportAbstraction ):
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

library( jsonlite )

data.DocTopicMatrix = model$theta
data.TermTopicMatrix = exp( t( model$beta$logbeta[[1]] ) )

# Document Index
temp.DocCount <- nrow(model$theta)
temp.DocIDs <- paste( "Document #", 1:temp.DocCount, sep = "" )
temp.DocIndex <- 1:temp.DocCount
temp.DocIndexValues <- cbind( temp.DocIndex, temp.DocIDs )
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

	def __init__( self, app_name, app_model = 'lda', app_desc = 'Structural Topic Model' ):
		ImportAbstraction.__init__( self, app_name, app_model, app_desc )

	def ImportLDA( self, model_filename ):
		self.GenerateR( model_filename )
	
	def GenerateR( self, model_filename ):
		r = ImportSTM.SCRIPT.format( DATA_PATH = self.data_path, MODEL_FILENAME = model_filename )
		script_filename = '{}/import.r'.format( self.data_path )
		with open( script_filename, 'w' ) as f:
			f.write( r.encode( 'utf-8' ) )
		
		command = [ 'RScript', script_filename ]
		print ' '.join(command)
		process = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
		while process.poll() is None:
			line = process.stderr.readline()
			print line[:-1]

def main():
	parser = argparse.ArgumentParser( description = 'Import a STM topic model as a web2py application.' )
	parser.add_argument( 'app_name'  , type = str, help = 'Web2py application identifier'               )
	parser.add_argument( 'model'     , type = str, help = 'File containing a STM model (RData)'         )
	args = parser.parse_args()
	
	importer = ImportSTM( args.app_name )
	importer.ImportLDA( args.model )
	importer.ResolveMatrices()
	importer.TransposeMatrices()
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
