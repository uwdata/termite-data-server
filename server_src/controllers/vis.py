#!/usr/bin/env python

from core import TermiteCore
from GroupInABox import GroupInABox as GroupInABoxModel
from CovariateChart import CovariateChart as CovariateChartModel

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

def CovariateChart():
	core = TermiteCore( request, response )
	chart = CovariateChartModel( request )
	topTerms = chart.GetTopTerms()
	docTopics = chart.GetDocTopics()
	return core.GenerateResponse( chart.params, {
		'TopTerms' : topTerms,
		'DocTopics' : docTopics
	})
