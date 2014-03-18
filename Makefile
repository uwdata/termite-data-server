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

data/demo/20newsgroups:
	bin/fetch_20newsgroups.sh

data/demo/infovis:
	bin/fetch_infovis.sh

data/demo/poliblogs:
	bin/fetch_poliblogs.sh

data/demo/nsf127992:
	bin/fetch_nsf127992.sh

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


################################################################################
# Other utilities

utils: utils/mallet/CorpusWriter.jar

utils/mallet/CorpusWriter.jar:
	$(MAKE) -C utils/mallet

################################################################################

clean:
	rm -rf externals
	rm -rf tools/mallet*
	rm -rf tools/stm*
	rm -rf data/demo/infovis apps/infovis_mallet web2py/applications/infovis_mallet
	rm -rf data/demo/poliblogs apps/poliblogs_stm web2py/applications/poliblogs_stm
