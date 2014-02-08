#!/usr/bin/env python

from core import TermiteCore
from lda import LDA

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()

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
		'TermTopicMatrix' : termTopicMatrix,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex
	})

