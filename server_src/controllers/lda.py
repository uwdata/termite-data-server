#!/usr/bin/env python

from core import TermiteCore
from lda import LDA

def index():
	core = TermiteCore( request, response )
	lda = LDA( request )
	params = lda.GetParams()
	return core.GenerateResponse( params )

def DocIndex():
	core = TermiteCore( request, response )
	lda = LDA( request )
	params = lda.GetParams()
	docIndex, docMaxCount = lda.GetDocIndex( params )
	return core.GenerateResponse( params, {
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'DocIndex' : docIndex
	})

def TermIndex():
	core = TermiteCore( request, response )
	lda = LDA( request )
	params = lda.GetParams()
	termIndex, termMaxCount = lda.GetTermIndex( params )
	return core.GenerateResponse( params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'TermIndex' : termIndex
	})

def TopicIndex():
	core = TermiteCore( request, response )
	lda = LDA( request )
	params = lda.GetParams()
	topicIndex, topicMaxCount = lda.GetTopicIndex( params )
	return core.GenerateResponse( params, {
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TopicIndex' : topicIndex
	})

def TermTopicMatrix():
	core = TermiteCore( request, response )
	lda = LDA( request )
	params = lda.GetParams()
	termIndex, termMaxCount = lda.GetTermIndex( params )
	topicIndex, topicMaxCount = lda.GetTopicIndex( params )
	termTopicMatrix = lda.GetTermTopicMatrix( params )
	return core.GenerateResponse( params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix
	})

def DocTopicMatrix():
	core = TermiteCore( request, response )
	lda = LDA( request )
	params = lda.GetParams()
	docIndex, docMaxCount = lda.GetDocIndex( params )
	topicIndex, topicMaxCount = lda.GetTopicIndex( params )
	docTopicMatrix = lda.GetDocTopicMatrix( params )
	return core.GenerateResponse( params, {
		'docCount' : len(docIndex),
		'docMaxCount' : docMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'DocIndex' : docIndex,
		'TopicIndex' : topicIndex,
		'DocTopicMatrix' : docTopicMatrix
	})
