#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers.Home_Core import Home_Core

class BOW_Core(Home_Core):
	def __init__(self, request, response, bow_db):
		super(BOW_Core, self).__init__(request, response)
		self.bowDB = bow_db
		self.db = bow_db.db
	
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

	def GetTermLimits(self):
		termOffset = self.GetNonNegativeIntegerParam('termOffset')
		termLimit = self.GetNonNegativeIntegerParam('termLimit')
		self.params.update({
			'termOffset' : termOffset,
			'termLimit' : termLimit
		})
		if termOffset is None:
			termOffset = 0
		if termLimit is None:
			termLimit = 5
		return termOffset, termLimit

	def GetCellLimits(self):
		cellLimit = self.GetNonNegativeIntegerParam('cellLimit')
		self.params.update({
			'cellLimit' : cellLimit
		})
		if cellLimit is None:
			cellLimit = 100
		return cellLimit

	def LoadTermStats( self, table_name, var_name, field_name ):
		termOffset, termLimit = self.GetTermLimits()
		query = """SELECT stats.value AS {FIELD}, ref.term_text AS term_text 
		FROM {TABLE} AS stats 
		INNER JOIN term_texts as ref ON stats.term_index = ref.term_index 
		ORDER BY stats.rank LIMIT {LIMIT} OFFSET {OFFSET}""".format(
			FIELD = field_name, TABLE = table_name, LIMIT = termLimit, OFFSET = termOffset )
		rows = self.db.executesql( query, as_dict = True )
		header = [
			{ 'name' : 'term_text', 'type' : self.db.term_texts.term_text.type },
			{ 'name' : field_name, 'type' : self.db[table_name].value.type }
		]
		self.content.update({
			var_name : rows,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
			'TermCount' : self.db(self.db.term_texts).count()
		})
		self.table = rows
		self.header = header
	
	def LoadCoTermStats( self, table_name, var_name ):
		termOffset, termLimit = self.GetTermLimits()
		query = """SELECT stats.value AS value, ref1.term_text AS first_term, ref2.term_text as second_term 
		FROM {TABLE} AS stats 
		INNER JOIN term_texts as ref1 ON stats.first_term_index = ref1.term_index 
		INNER JOIN term_texts as ref2 ON stats.second_term_index = ref2.term_index 
		ORDER BY stats.rank LIMIT {LIMIT} OFFSET {OFFSET}""".format(
			TABLE = table_name, LIMIT = termLimit, OFFSET = termOffset )
		rows = self.db.executesql( query, as_dict = True )
		header = [
			{ 'name' : 'first_term', 'type' : self.db.term_texts.term_text.type },
			{ 'name' : 'second_term', 'type' : self.db.term_texts.term_text.type },
			{ 'name' : 'value', 'type' : self.db[table_name].value.type }
		]
		self.content.update({
			var_name : rows,
			'TermLimit' : termLimit,
			'TermOffset' : termOffset,
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

	def LoadTermG2( self ):
		self.LoadCoTermStats( self.db.term_g2, 'TermG2' )

	def LoadSentenceCoFreqs( self ):
		self.LoadCoTermStats( self.db.sentences_co_freqs, 'SentenceCoFreqs' )

	def LoadSentenceCoProbs( self ):
		self.LoadCoTermStats( self.db.sentences_co_probs, 'SentenceCoProbs' )

	def LoadSentenceG2( self ):
		self.LoadCoTermStats( self.db.sentences_g2, 'SentenceG2' )
