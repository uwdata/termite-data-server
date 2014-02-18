#!/usr/bin/env python

from core import TermiteCore
from lda import LDA
from corpus import Corpus
from GroupInABox import GroupInABox as GroupInABoxModel

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()

def GroupInABox():
	core = TermiteCore( request, response )
	lda = LDA( request )
	giab = GroupInABoxModel( request )
	corpus = Corpus( request )
	params = lda.params
	params.update( corpus.params )
	termIndex, termMaxCount = lda.GetTermIndex( params )
	topicIndex, topicMaxCount = lda.GetTopicIndex( params )
	termTopicMatrix = lda.GetTermTopicMatrix( params )
	termCoFreqs = corpus.GetTermCoFreqs( params )
	topicCooccurrence = lda.GetTopicCooccurrence( params )
	topTermsPerTopic = giab.GetTopTermsPerTopic( params )
	return core.GenerateResponse( params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix,
		'TopTermsPerTopic' : topTermsPerTopic,
		'TermCoFreqs' : termCoFreqs,
		'TopicCooccurrence' : topicCooccurrence
	})
