#!/usr/bin/env python

import argparse
import json
import csv
import re

def KeyLookup( key ):
	if key == 'speech':
		return 'DocContent'
	if key == 'discourse':
		return 'DocID'
	return key

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
			else:
				record = {}
				for n, value in enumerate( values ):
					if n < len(header):
						key = header[n]
					else:
						key = u'field{:d}'.format( n+1 )
					key = KeyLookup(key)
					record[ key ] = value
				key = record[ 'DocID' ]
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
			key = KeyLookup(key)
			record = documents[ key ]
			f.write( u'{}\t{}\n'.format( record['DocID'], record['DocContent'] ).encode( 'utf-8' ) )

def WriteMeta( filename, header, keys, documents ):
	with open( filename, 'w' ) as f:
		f.write( u'{}\n'.format( u'\t'.join( [ KeyLookup(key) for key in header ] ) ).encode( 'utf-8' ) )

		for key in keys:
			key = KeyLookup(key)
			record = documents[ key ]
			values = [ record[KeyLookup(key)] for key in header ]
			f.write( u'{}\n'.format( u'\t'.join( values ) ).encode( 'utf-8' ) )

def main():
	parser = argparse.ArgumentParser( description = 'Convert a comma-separated file to tab-delimited file.' )
	parser.add_argument( 'input' , type = str, nargs = '?', default = 'data/demo/fomc/corpus/FOMC2.csv', help = 'Input filename'  )
	parser.add_argument( 'output', type = str, nargs = '?', default = 'data/demo/fomc/corpus/FOMC2.txt', help = 'Output filename' )
	parser.add_argument( 'meta'  , type = str, nargs = '?', default = 'data/demo/fomc/corpus/FOMC2-meta.txt', help = 'Output filename' )
	args = parser.parse_args()
	
	header, keys, documents = ReadCSV( args.input )
	header, documents = Sanitize( header, documents )
	WriteTSV( args.output, header, keys, documents )
	WriteMeta( args.meta, header, keys, documents )

if __name__ == '__main__':
	main()
