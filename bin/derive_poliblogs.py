#!/usr/bin/env python

import argparse
import json
import csv
import re

def GetDate( remainingDays ):
	daysOfMonth = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
	for m, days in enumerate(daysOfMonth):
		if remainingDays <= days:
			return 2008, m+1, remainingDays
		remainingDays -= days
	return None, None, None
	
def ReadCSV( filename ):
	with open( filename, 'rb' ) as f:
		header = None
		keys = []
		documents = {}
		reader = csv.reader( f, delimiter = ',', quotechar = '"' )
		for index, values in enumerate( reader ):
			values = [ d.decode( 'ascii', 'ignore' ) for d in values ]
			if header is None:
				header = values
				header.append( 'date' )
			else:
				record = {}
				for n, value in enumerate( values ):
					if n < len(header):
						key = header[n]
					else:
						key = u'field{:d}'.format( n+1 )
					record[ key ] = value
				assert 'DocID' in record
				assert 'DocContent' in record
				
				assert 'day' in record
				year, month, day = GetDate( int(record['day']) )
				record['day'] = int(record['day'])
				record['date'] = '{:04d}/{:02d}/{:02d}'.format( year, month, day )
				
				key = record['DocID']
				keys.append( key )
				documents[ key ] = record
	return header, keys, documents

def Sanitize( header, documents ):
	ALPHANUMERIC = re.compile( r'[\W]+' );
	SINGLE_LINE = re.compile( r'[\n\r\f\t]+' );
	for i, value in enumerate( header ):
		header[ i ] = ALPHANUMERIC.sub( '', value )
	for document in documents.itervalues():
		document['DocContent'] = SINGLE_LINE.sub( ' ', document['DocContent'] )
	return header, documents
	
def WriteTSV( filename, header, keys, documents ):
	with open( filename, 'w' ) as f:
		for key in keys:
			record = documents[ key ]
			f.write( u'{}\t{}\n'.format( record['DocID'], record['DocContent'] ).encode( 'utf-8' ) )

def WriteMeta( filename, header, keys, documents ):
	with open( filename, 'w' ) as f:
		f.write( u'{}\n'.format( u'\t'.join( header ) ).encode( 'utf-8' ) )

		for key in keys:
			record = documents[ key ]
			values = [ record[i] for i in header ]
			f.write( u'{}\n'.format( u'\t'.join( u'{}'.format(value) for value in values ) ).encode( 'utf-8' ) )

def WriteHeader( filename ):
	header = [
		{ 'name' : 'DocIndex'  , 'type' : 'number' },
		{ 'name' : 'DocContent', 'type' : 'string' },
		{ 'name' : 'DocID'     , 'type' : 'string' },
		{ 'name' : 'rating'    , 'type' : 'string' },
		{ 'name' : 'day'       , 'type' : 'number' },
		{ 'name' : 'blog'      , 'type' : 'string' },
		{ 'name' : 'date'      , 'type' : 'date'   }
	]
	with open(filename, 'w') as f:
		json.dump( header, f, indent = 2, encoding = 'utf-8', sort_keys = True )

def main():
	parser = argparse.ArgumentParser( description = 'Convert a comma-separated file to tab-delimited file.' )
	parser.add_argument( 'input' , type = str, nargs = '?', default = 'data/demo/poliblogs/corpus/poliblogs2008.csv', help = 'Input filename'  )
	parser.add_argument( 'output', type = str, nargs = '?', default = 'data/demo/poliblogs/corpus/poliblogs2008.txt', help = 'Output filename' )
	parser.add_argument( 'meta'  , type = str, nargs = '?', default = 'data/demo/poliblogs/corpus/poliblogs2008-meta.txt', help = 'Output filename' )
	parser.add_argument( 'header', type = str, nargs = '?', default = 'data/demo/poliblogs/corpus/poliblogs2008-meta.json', help = 'Output filename' )
	args = parser.parse_args()
	
	header, keys, documents = ReadCSV( args.input )
	header, documents = Sanitize( header, documents )
	WriteTSV( args.output, header, keys, documents )
	WriteMeta( args.meta, header, keys, documents )
	WriteHeader( args.header )

if __name__ == '__main__':
	main()
