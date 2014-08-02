{{
	import math
	import urllib
	import json

	def MakeParamTextArea(name, value, width = 200, height = 50):
		HTML = """<textarea name="{NAME}" onchange="updateParamTextInput('{NAME}',this)" style="width: {WIDTH}px; height: {HEIGHT}px; vertical-align: -{THIRD_HEIGHT}px; margin-bottom: 10px">{VALUE}</textarea>"""
		html = HTML.format(NAME = name, VALUE=value, WIDTH=width, HEIGHT=height, THIRD_HEIGHT=height/2-10)
		response.write(html, escape=False)
	pass

	def MakeParamTextInput(name, value, width = 200):
		HTML = """<input type="text" name="{NAME}" value="{VALUE}" onkeyup="updateParamTextInput('{NAME}',this)" style="width: {WIDTH}px; vertical-align: -4px"/>"""
		html = HTML.format(NAME = name, VALUE=value, WIDTH=width)
		response.write(html, escape=False)
	pass
	
	def MakeParamRange(name, value, count, width = 200):
		HTML = """
		<input type="range" name="{NAME}" value="{VALUE_NUM}" min="-1" max="{COUNT}" onchange="updateParamRange('{NAME}',this)" style="width: {WIDTH}px; vertical-align: -4px"/>
		<span class="{NAME}" style="font-weight: bold; color: #000">{VALUE_STR}</span>
		"""
		value_num = int(math.sqrt(value) * 1000) if value is not None else -1
		value_str = value if value is not None else "&mdash;"
		count_num = int(math.sqrt(count) * 1000)
		html = HTML.format(NAME = name, VALUE_NUM=value_num, VALUE_STR=value_str, COUNT=count_num, WIDTH=width)
		response.write(html, escape=False)
	pass
	
	def MakeParamSelect(name, value, options, width = 200):
		HEAD = """<select name={NAME} onchange="updateParamSelect('{NAME}',this)" style="width: {WIDTH}px">"""
		OPTION = """<option value="{OPT_VALUE}" {OPT_SELECTED}>{OPT_NAME}</option>"""
		FOOT = """</select>"""
		s = []
		s.append( HEAD.format(NAME=name, WIDTH=width) )
		for option in options:
			opt_name = option['name']
			opt_value = option['value']
			opt_selected = 'selected="selected"' if opt_value == value else ''
			s.append( OPTION.format(OPT_NAME=opt_name, OPT_VALUE=opt_value, OPT_SELECTED=opt_selected) )
		pass
		s.append( FOOT )
		html = '\n'.join(s)
		response.write(html, escape=False)
	pass
	
	def MakeParamFormat(json_only=False):
		if json_only:
			HTML = """
			<select name={NAME} onchange="updateParamFormat(this)" style="width: 200px">
				<option value="NONE">&mdash;</option>
				<option value="json">JSON Object</option>
			</select>
			"""
		else:
			HTML = """
			<select name={NAME} onchange="updateParamFormat(this)" style="width: 200px">
				<option value="NONE">&mdash;</option>
				<option value="json">JSON Object</option>
				<option value="csv">Comma-separated Spreadsheet</option>
				<option value="tsv">Tab-delimited Spreadhseet</option>
			</select>
			"""
		pass
		html = HTML.format(NAME = 'format')
		response.write(html, escape=False)
	pass

	def WriteURL( keysAndValues = {} ):
		urlStr = configs['url']
		queryStr = urllib.urlencode({key : (value.encode('utf-8') if isinstance(value,unicode) else value) for key, value in params.iteritems() if value is not None})
		s = urlStr if len(queryStr) == 0 else '{}?{}'.format(urlStr, queryStr)
		response.write(s, escape=False)
	pass

	def WriteJSON( data ):
		response.write( json.dumps(data, encoding='utf-8', indent=2, sort_keys=True), escape=False )
	pass
}}
