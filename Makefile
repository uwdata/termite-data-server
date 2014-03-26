# Makefile for Termite Data Server
#
# This file is intended for development use only.
# All tools and folder structures should be ready for use, as they're stored in the git repo.
#

################################################################################
# Default configuration
#   Install web2py framework
#   Install MALLET toolkit
#   Build all utilities
#   Build all demos

all: web2py tools/mallet utils demo

################################################################################
# Web framework

web2py:
	bin/setup_web2py.sh

################################################################################
# Topic modeling tools
#   mallet, treetm, stm, gensim, stmt

tools/mallet: utils
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

data/demo/20newsgroups:
	bin/fetch_20newsgroups.sh

data/demo/infovis:
	bin/fetch_infovis.sh

data/demo/poliblogs:
	bin/fetch_poliblogs.sh

data/demo/nsf146k:
	bin/fetch_nsf146k.sh

################################################################################
# Demos
#   Download and build an LDA model using the InfoVis dataset

demo: apps/infovis_mallet

demos: apps/infovis_mallet apps/infovis_gensim apps/poliblogs_stm

apps/infovis_mallet: web2py tools/mallet data/demo/infovis
	./demo infovis mallet

apps/infovis_gensim: web2py tools/gensim data/demo/infovis
	./demo infovis gensim

apps/poliblogs_stm: web2py tools/stm data/demo/poliblogs
	./demo poliblogs stm

other-demos:
	./demo infovis mallet
	./demo infovis gensim
	./demo poliblogs mallet
	./demo poliblogs gensim
	./demo poliblogs stm
	./demo fomc mallet
	./demo fomc gensim
	./demo fomc stm
	./demo 20newsgroups mallet
	bin/fetch_nsf146k.sh
	bin/derive_nsf1k.py
	./demo nsf1k mallet
	bin/derive_nsf10k.py
	./demo nsf10k mallet
	bin/derive_nsf25k.py
	./demo nsf25k mallet
	./demo nsf146k mallet

################################################################################
# Other utilities

utils: utils/mallet/CorpusWriter.jar utils/corenlp/SentenceSplitter.jar utils/corenlp/StreamingSentenceSplitter.jar

utils/mallet/CorpusWriter.jar:
	$(MAKE) -C utils/mallet

utils/corenlp/SentenceSplitter.jar:
	$(MAKE) -C utils/corenlp SentenceSplitter.jar

utils/corenlp/StreamingSentenceSplitter.jar:
	$(MAKE) -C utils/corenlp StreamingSentenceSplitter.jar

################################################################################

clean:
	rm -rf externals
