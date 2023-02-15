#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from past.utils import old_div
import sys
sys.path.append("web2py")

import json
import argparse
import logging
import os

from db.LDA_DB import LDA_DB
from readers.STMReader import STMReader

def main():
	parser = argparse.ArgumentParser(description = 'Import a STM topic model as a folder of files.')
	parser.add_argument('path', type = str , default = 'model_001', help = 'A folder containing file "stm.RData"')
	args = parser.parse_args()
	path = args.path

	logger = logging.getLogger('termite')
	logger.addHandler(logging.StreamHandler())
	logger.setLevel(logging.DEBUG)
	
	with LDA_DB(path, isInit=True) as lda_db:
		reader = STMReader(lda_db, path, None)
		reader.Execute()
	
	command = 'sqlite3 -separator "\t" {PATH}/lda.db "SELECT topic_index, term_text, value FROM term_topic_matrix INNER JOIN terms ON term_topic_matrix.term_index = terms.term_index ORDER BY topic_index ASC, value DESC" > {PATH}/topic-word-weights.txt'.format(PATH = path)
	logger.info(command)
	os.system(command)

	command = 'sqlite3 -separator "\t" {PATH}/lda.db "SELECT topic_index, SUM(value) FROM doc_topic_matrix GROUP BY topic_index ORDER BY topic_index" > {PATH}/topic-weights.txt'.format(PATH = path)
	logger.info(command)
	os.system(command)
	
	data = []
	max_value = 0
	filename = '{}/topic-weights.txt'.format(path)
	with open(filename, 'r') as f:
		for line in f.read().splitlines():
			topic_index, topic_weight = line.split('\t')
			topic_index = int(topic_index)
			topic_weight = float(topic_weight)
			max_value = max(topic_weight, max_value)
			data.append({
				"topic_index" : topic_index,
				"topic_weight" : topic_weight,
				"value" : topic_weight
			})
	for elem in data:
		elem['value'] = old_div(elem['value'], max_value)
	
	filename = '{}/meta.json'.format(path)
	with open(filename, 'w') as f:
		json.dump(data, f, encoding = 'utf-8', indent = 2, sort_keys = True)

if __name__ == '__main__':
	main()
