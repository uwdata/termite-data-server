{{
	def RenderSelectServer():
	pass



	import urllib
	def GenerateQueryString( keysAndValues = {} ):
		query = { key : request.vars[ key ] for key in request.vars }
		query.update( keysAndValues )
		for key in query.keys():
			if query[ key ] is None:
				del query[ key ]
			pass
		if len(query) > 0:
			return '?' + urllib.urlencode(query)
		return ''
		pass
	pass
	def WriteQueryString( keysAndValues = {} ):
		response.write( GenerateQueryString(keysAndValues), escape = False )
	pass
	def GenerateURL( keysAndValues = {} ):
		return configs['url'] + GenerateQueryString( keysAndValues )
	pass
	def WriteURL( keysAndValues = {} ):
		response.write( GenerateURL(keysAndValues), escape = False )
	pass
}}

{{
	import json
	def WriteJSON( data ):
		response.write( json.dumps( data, encoding = 'utf-8', indent = 2, sort_keys = True ), escape = False )
	pass
}}
