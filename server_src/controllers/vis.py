#!/usr/bin/env python

from core import TermiteCore
from GroupInABox import GroupInABox as GroupInABoxModel
from CovariateChart import CovariateChart as CovariateChartModel

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()

def GroupInABox():
	gib = GroupInABoxModel( request, response )
	gib.LoadTopTermsPerTopic()
	gib.LoadTopicCovariance()
	gib.LoadTermFreqs()
	gib.LoadTermCoFreqs()
	gib.LoadTermPMI()
	return gib.GenerateResponse()

def CovariateChart():
	chart = CovariateChartModel( request, response )
	chart.LoadDocTopicMatrix()
	chart.LoadTopicTopTerms()
	return chart.GenerateResponse()
