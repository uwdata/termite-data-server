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

# Doc-Topic Matrix
# Tab-seperated with no headers. Theta (D by K)
data.DocTopicMatrix = model$theta
write.table( data.DocTopicMatrix, file = app.path.DocTopicMatrix, quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE )

# Term-Topic Matrix
# Tab-separated with no headers. Beta (V by K)
data.TermTopicMatrix = exp( t( model$beta$logbeta[[1]] ) )
write.table( data.TermTopicMatrix, file = app.path.TermTopicMatrix, quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE )

library( jsonlite )

# Document Index
temp.DocCount <- dim(model$beta$logbeta[[1]])[2]
temp.DocIDs <- paste( "Document #", 1:temp.DocCount, sep = "" )
temp.DocIndexValues <- cbind( temp.DocIDs )
temp.DocIndexHeader <- c( "docID" )
colnames( temp.DocIndexValues ) <- temp.DocIndexHeader
data.DocIndexJSON <- toJSON( as.data.frame( temp.DocIndexValues ), pretty = TRUE )
write( data.DocIndexJSON, file = app.path.DocIndex )

# Term Index
temp.TermFreq <- apply( model$beta$logbeta[[1]], 2, sum )   # Cannot retrieve beta???
temp.TermText <- model$vocab
temp.TermIndexValues = cbind( temp.TermFreq, temp.TermText )
temp.TermIndexHeader = c( "freq", "text" )
colnames( temp.TermIndexValues ) <- temp.TermIndexHeader
data.TermIndexJSON <- toJSON( as.data.frame( temp.TermIndexValues ), pretty = TRUE )
write( data.TermIndexJSON, file = app.path.TermIndex )

# Topic Index
temp.TopicFreq <- apply( model$beta$logbeta[[1]], 1, sum )   # Cannot retrieve beta???
temp.TopicIndex <- 1:length(temp.TopicFreq)
temp.TopicIndexValues = cbind( temp.TopicFreq, temp.TopicIndex )
temp.TopicIndexHeader = c( "freq", "index" )
colnames( temp.TopicIndexValues ) <- temp.TopicIndexHeader
data.TopicIndexJSON <- toJSON( as.data.frame( temp.TermIndexValues ), pretty = TRUE )
write( data.TopicIndexJSON, file = app.path.TopicIndex )
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
	importer.AddToWeb2py()

if __name__ == '__main__':
	main()
