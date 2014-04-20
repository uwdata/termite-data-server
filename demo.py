#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import subprocess

DEFAULT_DATASET = 'infovis'
DATASETS = [ DEFAULT_DATASET, '20newsgroups', 'nsf146k', 'nsf25k', 'nsf10k', 'nsf1k', 'poliblogs', 'fomc' ]

DEFAULT_MODEL = 'mallet'
MODELS = [ DEFAULT_MODEL, 'treetm', 'stmt', 'stm', 'gensim' ]

def Execute(command):
	p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	while p.poll() is None:
		print p.stdout.readline().rstrip('\n')

def Demonstrate(dataset, model, is_quiet, force_overwrite):
	database_filename = 'data/demo/{}/corpus/corpus.db'.format(dataset)
	corpus_filename = 'data/demo/{}/corpus/corpus.txt'.format(dataset)
	model_folder = 'data/demo/{}/model-{}'.format(dataset, model)
	app_name = '{}_{}'.format(dataset, model)

	def PrepareDataset():
		Execute(['bin/fetch_dataset.sh', dataset])
	
	def PrepareModel():
		binary = 'bin/setup_{}.sh'.format(model)
		Execute([binary])
	
	def PrepareOthers():
		Execute(['bin/setup_corenlp.sh'])
	
	def ExtractCorpus():
		Execute(['bin/export_corpus.py', database_filename, corpus_filename])
	
	def TrainModel():
		binary = 'bin/train_{}.py'.format(model)
		if model == 'stm':
			corpus_folder = 'data/demo/{}/corpus'.format(dataset)
			command = [binary, corpus_folder, model_folder]
		else:
			command = [binary, corpus_filename, model_folder]
		if is_quiet:
			command.append('--quiet')
		if force_overwrite:
			command.append('--overwrite')
		Execute(command)

	def ImportModel():
		binary = 'bin/import_{}.py'.format(model)
		command = [binary, app_name, model_folder, corpus_filename, database_filename]
		if is_quiet:
			command.append('--quiet')
		if force_overwrite:
			command.append('--overwrite')
		Execute(command)

	print '--------------------------------------------------------------------------------'
	print 'Build a topic model ({}) using a demo dataset ({})'.format(model, dataset)
	print 'database = {}'.format(database_filename)
	print '  corpus = {}'.format(corpus_filename)
	print '   model = {}'.format(model_folder)
	print '     app = {}'.format(app_name)
	print '--------------------------------------------------------------------------------'
	
	PrepareDataset()
	PrepareModel()
	PrepareOthers()
	ExtractCorpus()
	TrainModel()
	ImportModel()
	
def main():
	parser = argparse.ArgumentParser( description = 'Import a MALLET topic model as a web2py application.' )
	parser.add_argument( 'dataset'     , nargs = '?', type = str, default = DEFAULT_DATASET, choices = DATASETS, help = 'Dataset identifier' )
	parser.add_argument( 'model'       , nargs = '?', type = str, default = DEFAULT_MODEL  , choices = MODELS  , help = 'Model type' )
	parser.add_argument( '--quiet'     , const = True, default = False, action = 'store_const', help = 'Show fewer debugging messages' )
	parser.add_argument( '--overwrite' , const = True, default = False, action = 'store_const', help = 'Overwrite any existing model'  )
	args = parser.parse_args()
	Demonstrate( args.dataset, args.model, args.quiet, args.overwrite )

if __name__ == '__main__':
	main()
