#!/usr/bin/env python

class TreeTM:
	def __init__( self, request ):
		self.request = request
		self.params = self.GetParams()

	def GetParams( self ):
		def GetString( key, defaultValue ):
			if key in self.request.vars:
				return self.request.vars[key]
			else:
				return defaultValue
			
		return {
			'termTopicPromotions' : GetString( 'termTopicPromotions', '' ),
			'termTopicDemotions' : GetString( 'termTopicDemotions', '' ),
			'termExclusions' : GetString( 'termExclusions', '' )
		}
