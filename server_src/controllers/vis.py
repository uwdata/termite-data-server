#!/usr/bin/env python

from core import TermiteCore
from lda import LDA
from corpus import Corpus
from group_box import GroupBox

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()

def GroupInABox():
	core = TermiteCore( request, response )
	lda = LDA( request )
	corpus = Corpus( request )
	params = lda.params
	params.update( corpus.params )
	termIndex, termMaxCount = lda.GetTermIndex( params )
	topicIndex, topicMaxCount = lda.GetTopicIndex( params )
	termTopicMatrix = lda.GetTermTopicMatrix( params )
	termCoFreqs = corpus.GetTermCoFreqs( params )
	topicCooccurrence = lda.GetTopicCooccurrence( params )
	return core.GenerateResponse( params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix,
		'TermCoFreqs' : termCoFreqs,
		'TopicCooccurrence' : topicCooccurrence
	})
