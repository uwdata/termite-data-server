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

demo:
	./demo infovis mallet

demos:
	./demo infovis mallet
	./demo infovis gensim
	./demo poliblogs stm

all-demos:
	./demo infovis mallet
	./demo infovis gensim
	./demo infovis treetm
	./demo poliblogs mallet
	./demo poliblogs gensim
	./demo poliblogs treetm
	./demo poliblogs stm
	./demo fomc mallet
	./demo fomc gensim
	./demo fomc treetm
	./demo fomc stm
	./demo 20newsgroups mallet
	./demo 20newsgroups gensim
	./demo 20newsgroups treetm
	./demo nsf146k mallet
	./demo nsf146k gensim
	./demo nsf146k treetm

other-demos:
	bin/fetch_nsf146k.sh
	bin/derive_nsf1k.py
	./demo nsf1k mallet
	./demo nsf1k treetm
	bin/derive_nsf10k.py
	./demo nsf10k mallet
	./demo nsf10k treetm
	bin/derive_nsf25k.py
	./demo nsf25k mallet
	./demo nsf25k treetm
	./demo nsf146k mallet
	./demo nsf146k treetm

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
