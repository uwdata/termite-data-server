#!/usr/bin/env python

from core import TermiteCore
from group_box import GroupBox

def index():
	core = TermiteCore( request, response )
	group_box = GroupBox( request )
	return core.GenerateResponse( group_box.params )

def TermTopicData():
	core = TermiteCore( request, response )
	group_box = GroupBox( request )
	termIndex, termMaxCount = group_box.GetTermIndex()
	topicIndex, topicMaxCount = group_box.GetTopicIndex()
	termTopicMatrix = group_box.GetTermTopicMatrix()
	termCooccurrence = group_box.GetTermCooccurrence()
	topicCooccurrence = group_box.GetTopicCooccurrence()
	return core.GenerateResponse( group_box.params, {
		'termCount' : len(termIndex),
		'termMaxCount' : termMaxCount,
		'topicCount' : len(topicIndex),
		'topicMaxCount' : topicMaxCount,
		'TermIndex' : termIndex,
		'TopicIndex' : topicIndex,
		'TermTopicMatrix' : termTopicMatrix,
		'TermCooccurrence' : termCooccurrence,
		'TopicCooccurrence' : topicCooccurrence
	})
