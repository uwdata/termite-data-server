#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("web2py")

import argparse
import logging
import os

from db.LDA_DB import LDA_DB
from readers.GensimReader import GensimReader

def main():
	parser = argparse.ArgumentParser(description = 'Import a gensim topic model as a folder of files.')
	parser.add_argument('path', type = str , default = 'model_001', help = 'A folder containing files "gensim.dict" and "gensim.model"')
	args = parser.parse_args()
	path = args.path

	logger = logging.getLogger('termite')
	logger.addHandler(logging.StreamHandler())
	logger.setLevel(logging.DEBUG)
	
	with LDA_DB(path, isInit=True) as lda_db:
		reader = GensimReader(lda_db, path, None, extraStateFile = True)
		reader.Execute()

	command = 'sqlite3 -separator "\t" {PATH}/lda.db "SELECT topic_index, term_text, value FROM term_topic_matrix INNER JOIN terms ON term_topic_matrix.term_index = terms.term_index ORDER BY topic_index ASC, value DESC" > {PATH}/topic-word-weights.txt'.format(PATH = path)
	logger.info(command)
	os.system(command)

if __name__ == '__main__':
	main()
