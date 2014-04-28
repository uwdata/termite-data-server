#!/usr/bin/env python

import re
import os
import json
from handlers.Home_Core import Home_Core

class Corpus_Core( Home_Core ):
	def __init__( self, request, response, corpus_db ):
		super( Corpus_Core, self ).__init__( request, response )
		self.db = corpus_db.db
	
	def GetDocLimits(self):
		docOffset = self.GetNonNegativeIntegerParam( 'docOffset', 0 )
		docLimit = self.GetNonNegativeIntegerParam( 'docLimit', 100 if self.IsMachineFormat() else 5 )
		self.params.update({
			'docOffset' : docOffset,
			'docLimit' : docLimit
		})
		return docOffset, docOffset+docLimit

	def GetTermLimits(self):
		termOffset = self.GetNonNegativeIntegerParam( 'termOffset', 0 )
		termLimit = self.GetNonNegativeIntegerParam( 'termLimit', 100 if self.IsMachineFormat() else 5 )
		self.params.update({
			'termOffset' : termOffset,
			'termLimit' : termLimit
		})
		return termOffset, termOffset+termLimit

	def GetDocIndex(self):
		docIndex = self.GetNonNegativeIntegerParam( 'docIndex', 0 )
		self.params.update({
			'docIndex' : docIndex
		})
		return docIndex

	def GetDocId(self):
		docId = self.GetStringParam( 'docId' )
		self.params.update({
			'docId' : docId
		})
		return docId

	def GetSearchPattern(self):
		searchPattern = self.GetStringParam( 'searchPattern' )
		self.params.update({
			'searchPattern' : searchPattern
		})
		return searchPattern
	
	def LoadMetadataFields( self ):
		table = self.db.fields
		rows = self.db().select( table.ALL, orderby = table.field_index ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Fields' : rows
		})
		self.table = rows
		self.header = header
	
	def LoadDocumentByIndex( self ):
		term_limits = self.GetTermLimits()
		doc_index = self.GetDocIndex()
		table = self.db.corpus
		where = (table.doc_index == doc_index)
		rows = self.db( where ).select( table.ALL, orderby = table.doc_index, limitby = term_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Document' : rows
		})
		self.table = rows
		self.header = header
	
	def LoadDocumentById( self ):
		term_limits = self.GetTermLimits()
		doc_id = self.GetDocId()
		table = self.db.corpus
		where = (table.doc_id == doc_id)
		rows = self.db( where ).select( table.ALL, orderby = table.doc_id, limitby = term_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Document' : rows
		})
		self.table = rows
		self.header = header
	
	def SearchDocuments( self ):
		doc_limits = self.GetDocLimits()
		search_pattern = self.GetSearchPattern()
		table = self.db.corpus
		where = table.doc_content.like('' if len(search_pattern) == 0 else '%'+search_pattern+'%')
		rows = self.db( where ).select( table.ALL, orderby = table.doc_index, limitby = doc_limits ).as_list()
		header = [ { 'name' : field, 'type' : table[field].type } for field in table.fields ]
		self.content.update({
			'Documents' : rows
		})
		self.table = rows
		self.header = header
		
	def LoadTermStats( self, table_name, var_name, field_name ):
		term_limits = self.GetTermLimits()
		query = """SELECT stats.value AS {FIELD}, ref.term_text AS term_text 
		FROM {TABLE} AS stats 
		INNER JOIN term_texts as ref ON stats.term_index = ref.term_index 
		ORDER BY stats.rank LIMIT {LIMIT} OFFSET {OFFSET}""".format(
			FIELD = field_name, TABLE = table_name, LIMIT = term_limits[1]-term_limits[0], OFFSET = term_limits[0] )
		rows = self.db.executesql( query, as_dict = True )
		header = [
			{ 'name' : 'term_text', 'type' : self.db.term_texts.term_text.type },
			{ 'name' : field_name, 'type' : self.db[table_name].value.type }
		]
		self.content.update({
			var_name : rows,
			'TermCount' : self.db(self.db.term_texts).count()
		})
		self.table = rows
		self.header = header
	
	def LoadCoTermStats( self, table_name, var_name ):
		term_limits = self.GetTermLimits()
		query = """SELECT stats.value AS value, ref1.term_text AS first_term, ref2.term_text as second_term 
		FROM {TABLE} AS stats 
		INNER JOIN term_texts as ref1 ON stats.first_term_index = ref1.term_index 
		INNER JOIN term_texts as ref2 ON stats.second_term_index = ref2.term_index 
		ORDER BY stats.rank LIMIT {LIMIT} OFFSET {OFFSET}""".format(
			TABLE = table_name, LIMIT = term_limits[1]-term_limits[0], OFFSET = term_limits[0] )
		rows = self.db.executesql( query, as_dict = True )
		header = [
			{ 'name' : 'first_term', 'type' : self.db.term_texts.term_text.type },
			{ 'name' : 'second_term', 'type' : self.db.term_texts.term_text.type },
			{ 'name' : 'value', 'type' : self.db[table_name].value.type }
		]
		self.content.update({
			var_name : rows,
			'CellCount' : self.db(self.db[table_name]).count(),
			'TermCount' : self.db(self.db.term_texts).count()
		})
		self.table = rows
		self.header = header

	def LoadTermFreqs( self ):
		self.LoadTermStats( self.db.term_freqs, 'TermFreqs', 'term_freq' )

	def LoadTermProbs( self ):
		self.LoadTermStats( self.db.term_probs, 'TermProbs', 'term_prob' )

	def LoadTermCoFreqs( self ):
		self.LoadCoTermStats( self.db.term_co_freqs, 'TermCoFreqs' )

	def LoadTermCoProbs( self ):
		self.LoadCoTermStats( self.db.term_co_probs, 'TermCoProbs' )

	def LoadTermPMI( self ):
		self.LoadCoTermStats( self.db.term_pmi, 'TermPMI' )

	def LoadTermG2( self ):
		self.LoadCoTermStats( self.db.term_g2, 'TermG2' )

	def LoadSentenceCoFreqs( self ):
		self.LoadCoTermStats( self.db.sentences_co_freqs, 'SentenceCoFreqs' )

	def LoadSentenceCoProbs( self ):
		self.LoadCoTermStats( self.db.sentences_co_probs, 'SentenceCoProbs' )

	def LoadSentencePMI( self ):
		self.LoadCoTermStats( self.db.sentences_pmi, 'SentencePMI' )

	def LoadSentenceG2( self ):
		self.LoadCoTermStats( self.db.sentences_g2, 'SentenceG2' )
