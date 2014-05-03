#!/usr/bin/env python

from handlers.Home_Core import Home_Core

class Corpus_Core( Home_Core ):
	def __init__( self, request, response, corpus_db ):
		super( Corpus_Core, self ).__init__( request, response )
		self.db = corpus_db.db
	
	def GetDocLimits(self):
		docOffset = self.GetNonNegativeIntegerParam('docOffset')
		docLimit = self.GetNonNegativeIntegerParam('docLimit')
		self.params.update({
			'docOffset' : docOffset,
			'docLimit' : docLimit
		})
		if docOffset is None:
			docOffset = 0
		if docLimit is None:
			docLimit = 5
		return docOffset, docLimit

	def GetDocIndex(self):
		docIndex = self.GetNonNegativeIntegerParam('docIndex')
		self.params.update({
			'docIndex' : docIndex
		})
		if docIndex is None:
			docIndex = 0
		return docIndex

	def GetDocId(self):
		docId = self.GetStringParam('docId')
		self.params.update({
			'docId' : docId
		})
		if docId is None:
			docId = ''
		return docId

	def GetSearchPattern(self):
		searchPattern = self.GetStringParam( 'searchPattern' )
		self.params.update({
			'searchPattern' : searchPattern
		})
		if searchPattern is None:
			searchPattern = ''
		return searchPattern
	
	def LoadMetadataFields( self ):
		table = self.db.fields
		rows = self.db().select( table.ALL, orderby = table.field_index ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Metadata' : rows
		})
		self.table = rows
		self.header = header
	
	def LoadDocumentByIndex( self ):
		docIndex = self.GetDocIndex()
		docCount = self.db(self.db.corpus).count()
		table = self.db.corpus
		where = (table.doc_index == docIndex)
		rows = self.db( where ).select( table.ALL, orderby = table.doc_index ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Document' : rows,
			'DocIndex' : docIndex,
			'DocCount' : docCount
		})
		self.table = rows
		self.header = header
	
	def LoadDocumentById( self ):
		docId = self.GetDocId()
		table = self.db.corpus
		where = (table.doc_id == docId)
		rows = self.db( where ).select( table.ALL, orderby = table.doc_id ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Document' : rows,
			'DocId' : docId
		})
		self.table = rows
		self.header = header
	
	def SearchDocuments( self ):
		docOffset, docLimit = self.GetDocLimits()
		docCount = self.db(self.db.corpus).count()
		searchPattern = self.GetSearchPattern()
		table = self.db.corpus
		where = table.doc_content.like('' if len(searchPattern) == 0 else '%'+searchPattern+'%')
		rows = self.db( where ).select( table.ALL, orderby = table.doc_index, limitby = (docOffset, docOffset+docLimit) ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Documents' : rows,
			'SearchPattern' : searchPattern,
			'DocOffset' : docOffset,
			'DocLimit' : docLimit,
			'DocCount' : docCount
		})
		self.table = rows
		self.header = header
