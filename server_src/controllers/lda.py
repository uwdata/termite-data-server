#!/usr/bin/env python

from lda import LDA

def index():
	lda = LDA( request, response )
	return lda.GenerateResponse()

def TermIndex():
	lda = LDA( request, response )
	lda.LoadTermIndex()
	return lda.GenerateResponse()

def DocIndex():
	lda = LDA( request, response )
	lda.LoadDocIndex()
	return lda.GenerateResponse()

def TopicIndex():
	lda = LDA( request, response )
	lda.LoadTopicIndex()
	return lda.GenerateResponse()

def TermTopicMatrix():
	lda = LDA( request, response )
	lda.LoadTermTopicMatrix()
	return lda.GenerateResponse()

def DocTopicMatrix():
	lda = LDA( request, response )
	lda.LoadDocTopicMatrix()
	return lda.GenerateResponse()

def TopicTermMatrix():
	lda = LDA( request, response )
	lda.LoadTopicTermMatrix()
	return lda.GenerateResponse()

def TopicDocMatrix():
	lda = LDA( request, response )
	lda.LoadTopicDocMatrix()
	return lda.GenerateResponse()

def TopicCooccurrence():
	lda = LDA( request, response )
	lda.LoadTopicCooccurrence()
	return lda.GenerateResponse()

def TopicCovariance():
	lda = LDA( request, response )
	lda.LoadTopicCovariance()
	return lda.GenerateResponse()

def TopicTopTerms():
	lda = LDA( request, response )
	lda.LoadTopicTopTerms()
	return lda.GenerateResponse()

def TopicTopDocs():
	lda = LDA( request, response )
	lda.LoadTopicTopDocs()
	return lda.GenerateResponse()
