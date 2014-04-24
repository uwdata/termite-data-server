#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import subprocess

class STMReader():
	"""
	modelPath = a model folder containing an R datafile stm.RData
	LDA_DB = a SQLite3 database
	"""
	
	THRESHOLD = 1e-5
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

	def __init__( self, modelPath, LDA_DB ):
		self.logger = logging.getLogger('termite')
		self.modelPath = modelPath
		self.modelRData = '{}/{}'.format( self.modelPath, STMReader.RDATA_FILENAME )
		self.modelScript = '{}/import.r'.format( self.modelPath )
		self.ldaTermTopicMatrix = '{}/term-topic-matrix.txt'.format( self.modelPath )
		self.ldaDocTopicMatrix = '{}/doc-topic-matrix.txt'.format( self.modelPath )
		self.ldaDocIndex = '{}/doc-index.json'.format( self.modelPath )
		self.ldaTermIndex = '{}/term-index.json'.format( self.modelPath )
		self.ldaTopicIndex = '{}/topic-index.json'.format( self.modelPath )
		self.ldaDB = LDA_DB

	def Execute( self ):
		self.WriteToDisk()
		self.ReadFromDisk()
		self.GetTopTerms()
		self.SaveToDB()
	
	def WriteToDisk( self ):
		self.logger.info( 'Generating R script: %s', self.modelScript )
		r = STMReader.SCRIPT.format( DATA_PATH = self.modelPath, MODEL_FILENAME = self.modelRData )
		with open( self.modelScript, 'w' ) as f:
			f.write( r.encode( 'utf-8' ) )
		self.logger.info( 'Executing R script: %s', self.modelScript )
		command = [ 'RScript', self.modelScript ]
		self.RunCommand( command )
	
	def ReadFromDisk( self ):
		with open( self.ldaTermTopicMatrix ) as f:
			self.termTopicMatrix = json.load( f, encoding = 'utf-8' )
		with open( self.ldaDocTopicMatrix ) as f:
			self.docTopicMatrix = json.load( f, encoding = 'utf-8' )
		with open( self.ldaDocIndex ) as f:
			self.docIndex = json.load( f, encoding = 'utf-8' )
		with open( self.ldaTermIndex ) as f:
			self.termIndex = json.load( f, encoding = 'utf-8' )
		with open( self.ldaTopicIndex ) as f:
			self.topicIndex = json.load( f, encoding = 'utf-8' )
		self.docCount = len(self.docIndex)
		self.termCount = len(self.termIndex)
		self.topicCount = len(self.topicIndex)
	
	def GetTopTerms( self ):
		self.topTerms = []
		for topic in range(self.topicCount):
			topTerms = [ { 'index' : termIndex, 'freq' : d[topic] } for termIndex, d in enumerate(self.termTopicMatrix) ]
			self.topTerms.append( [ d['index'] for d in sorted( topTerms, key = lambda x : -x['freq'] ) ] )
			
	def SaveToDB( self ):
		termTable = []
		docTable = []
		topicTable = []
		for termObject in self.termIndex:
			text = termObject['text']
			index = int(termObject['index'])
			termTable.append({
				'term_index' : index,
				'term_text' : text
			})
		for docObject in self.docIndex:
			index = int(docObject['index'])
			docTable.append({
				'doc_index' : index
			})
		for topic, topicObject in enumerate(self.topicIndex):
			index = int(topicObject['index'])
			freq = float(topicObject['freq'])
			topicTable.append({
				'topic_index' : index,
				'topic_freq' : freq,
				'topic_desc' : u', '.join(termTable[d]['term_text'] for d in self.topTerms[topic][:5]),
				'topic_top_terms' : [termTable[d]['term_text'] for d in self.topTerms[topic][:30]]
			})
		termIndexes = self.ldaDB.db.terms.bulk_insert(termTable)
		docIndexes = self.ldaDB.db.docs.bulk_insert(docTable)
		topicIndexes = self.ldaDB.db.topics.bulk_insert(topicTable)

		termTopicMatrix = []
		docTopicMatrix = []
		for term, topicFreqs in enumerate(self.termTopicMatrix):
			for topic, freq in enumerate(topicFreqs):
				if freq > STMReader.THRESHOLD:
					termTopicMatrix.append({
						'term_index' : term,
					 	'topic_index' : topic,
						'value' : freq
					})
		for doc, topicFreqs in enumerate(self.docTopicMatrix):
			for topic, freq in enumerate(topicFreqs):
				if freq > STMReader.THRESHOLD:
					docTopicMatrix.append({
						'doc_index' : doc,
					 	'topic_index' : topic,
						'value' : freq
					})
		termTopicMatrix.sort( key = lambda x : -x['value'] )
		docTopicMatrix.sort( key = lambda x : -x['value'] )
		self.ldaDB.db.term_topic_matrix.bulk_insert(termTopicMatrix)
		self.ldaDB.db.doc_topic_matrix.bulk_insert(docTopicMatrix)
		
	def RunCommand( self, command ):
		p = subprocess.Popen( command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
		while p.poll() is None:
			line = p.stdout.readline().rstrip('\n')
			if len(line) > 0:
				self.logger.debug( line )

