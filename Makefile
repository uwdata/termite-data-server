# Makefile for Termite Data Server
#
# This file is intended for development use only.
# All tools and folder structures should be ready for use, as they're stored in the git repo.
#

################################################################################
# Default configuration
#   Install web2py framework
#   Install MALLET toolkit
#   Build all demos

all: web2py tools/mallet demo

################################################################################
# Web framework

web2py:
	bin/setup_web2py.sh

################################################################################
# Topic modeling tools
#   mallet, treetm, stm, gensim, stmt

tools/mallet:
	bin/setup_mallet.sh

tools/treetm:
	bin/setup_treetm.sh

tools/stm:
	bin/setup_stm.sh

tools/gensim:
	bin/setup_gensim.sh

tools/stmt:
	bin/setup_stmt.sh

################################################################################
# Datasets

data/demo/infovis:
	mkdir -p data
	mkdir -p data/demo
	bin/fetch_infovis.sh data/demo/infovis

data/demo/poliblogs:
	mkdir -p data
	mkdir -p data/demo
	bin/fetch_poliblogs.sh data/demo/poliblogs

################################################################################
# Demos
#   Download and build an LDA model using the InfoVis dataset

demo: apps/infovis_mallet

stm: apps/poliblogs_stm

apps/infovis_mallet: web2py tools/mallet data/demo/infovis
	./demo.sh infovis mallet

apps/poliblogs_stm: web2py tools/stm data/demo/poliblogs
	bin/import_stm.py poliblogs_stm data/demo/poliblogs/corpus/poliblogs2008.RData
	bin/import_corpus.py poliblogs_stm --csv data/demo/poliblogs/corpus/poliblogs2008.csv

################################################################################

clean:
	rm -rf externals
	rm -rf web2py
	rm -rf tools/mallet*
	rm -rf data/demo/infovis apps/infovis_mallet web2py/applications/infovis_mallet
	rm -rf data/demo/poliblogs apps/poliblogs_stm web2py/applications/poliblogs_stm
