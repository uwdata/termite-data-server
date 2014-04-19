#!/usr/bin/env python

from lda import LDA
import random

def index():
	lda = LDA( request, response )
	return lda.GenerateResponse()

def TermIndex():
	lda = LDA( request, response )
	lda.LoadTermIndex()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def DocIndex():
	lda = LDA( request, response )
	lda.LoadDocIndex()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def TopicIndex():
	lda = LDA( request, response )
	lda.LoadTopicIndex()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def TermTopicMatrix():
	lda = LDA( request, response )
	lda.LoadTermTopicMatrix()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def DocTopicMatrix():
	lda = LDA( request, response )
	lda.LoadDocTopicMatrix()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def TopicCooccurrence():
	lda = LDA( request, response )
	lda.LoadTopicCooccurrence()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def TopicCovariance():
	lda = LDA( request, response )
	lda.LoadTopicCovariance()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def TopTerms():
	lda = LDA( request, response )
	lda.LoadTopTerms()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def TopDocs():
	lda = LDA( request, response )
	lda.LoadTopDocs()
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()

def Update():
	lda = LDA( request, response )
	lda.content['IterIndex'] = random.randint( 0, 10 )
	lda.content['IterCount'] = random.randint( 0, 1000 )
	return lda.GenerateResponse()
	