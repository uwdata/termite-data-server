#!/usr/bin/env python

from core import TermiteCore
from lda import LDA

def index():
	core = TermiteCore( request, response )
	lda = LDA( request )
	return core.GenerateResponse( lda.params )

def DocIndex():
	core = TermiteCore( request, response )
	lda = LDA( request )
	docIndex, docMaxCount = lda.GetDocIndex()
	return core.GenerateResponse( lda.params, {
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'DocIndex' : docIndex
	})

def TermIndex():
	core = TermiteCore( request, response )
	lda = LDA( request )
	termIndex, termMaxCount = lda.GetTermIndex()
	return core.GenerateResponse( lda.params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'TermIndex' : termIndex
	})

def TopicIndex():
	core = TermiteCore( request, response )
	lda = LDA( request )
	topicIndex, topicMaxCount = lda.GetTopicIndex()
	return core.GenerateResponse( lda.params, {
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TopicIndex' : topicIndex
	})

def TermTopicMatrix():
	core = TermiteCore( request, response )
	lda = LDA( request )
	termIndex, termMaxCount = lda.GetTermIndex()
	topicIndex, topicMaxCount = lda.GetTopicIndex()
	termTopicMatrix = lda.GetTermTopicMatrix()
	return core.GenerateResponse( lda.params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermTopicMatrix' : termTopicMatrix
	})

def DocTopicMatrix():
	core = TermiteCore( request, response )
	lda = LDA( request )
	docIndex, docMaxCount = lda.GetDocIndex()
	topicIndex, topicMaxCount = lda.GetTopicIndex()
	docTopicMatrix = lda.GetDocTopicMatrix()
	return core.GenerateResponse( lda.params, {
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'DocTopicMatrix' : docTopicMatrix
	})

def TopicCooccurrence():
	core = TermiteCore( request, response )
	lda = LDA( request )
	topicCooccurrence = lda.GetTopicCooccurrence()
	return core.GenerateResponse( lda.params, {
		'TopicCooccurrence' : topicCooccurrence
	})

