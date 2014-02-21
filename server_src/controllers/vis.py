#!/usr/bin/env python

from core import TermiteCore
from GroupInABox import GroupInABox as GroupInABoxModel

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()

def GroupInABox():
	core = TermiteCore( request, response )
	giab = GroupInABoxModel( request )
	topicCooccurrence = giab.GetTopicCooccurrence()
	topTermsPerTopic, termSet = giab.GetTopTermsPerTopic()
	termCoFreqs = giab.GetTermCoFreqs( termSet = termSet )
	return core.GenerateResponse( giab.params, {
		'TopTermsPerTopic' : topTermsPerTopic,
		'TermCoFreqs' : termCoFreqs,
		'TopicCooccurrence' : topicCooccurrence
	})
