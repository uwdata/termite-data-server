#!/usr/bin/env python

from vis.GroupInABox import GroupInABox as GroupInABoxModel
from vis.CovariateChart import CovariateChart as CovariateChartModel

def index():
	core = TermiteCore()
	return core.GenerateResponse()

def GroupInABox():
	gib = GroupInABoxModel()
	gib.Load()
	gib.LoadTopTermsPerTopic()
	gib.LoadTopicCovariance()
	gib.LoadTermFreqs()
	gib.LoadTermCoFreqs()
	gib.LoadTermProbs()
	gib.LoadTermPMI()
	gib.LoadTermSentencePMI()
	return gib.GenerateResponse()
