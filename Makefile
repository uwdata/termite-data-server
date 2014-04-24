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

all: web2py tools utils

################################################################################
# Web framework

web2py:
	bin/setup_web2py.sh

################################################################################
# Topic modeling tools
#   mallet, treetm, stm, gensim, stmt

tools: tools/mallet tools/treetm tools/stm tools/gensim tools/stmt tools/corenlp

tools/corenlp: utils
	bin/setup_corenlp.sh

tools/gensim:
	bin/setup_gensim.sh

tools/mallet: utils
	bin/setup_mallet.sh

tools/stmt:
	bin/setup_stmt.sh

tools/stm:
	bin/setup_stm.sh

tools/treetm:
	bin/setup_treetm.sh

################################################################################
# Demos
#   Download and build an LDA model using a provided dataset

demo:
	./demo.py infovis mallet

demos:
	./demo.py infovis gensim
	./demo.py poliblogs stm
	./demo.py infovis treetm

all-demos:
	./demo.py infovis mallet
	./demo.py infovis gensim
	./demo.py infovis treetm
	./demo.py nsf1k mallet
	./demo.py nsf1k treetm
	./demo.py nsf10k mallet
	./demo.py nsf10k treetm
	./demo.py nsf25k mallet
	./demo.py nsf25k treetm
	./demo.py poliblogs mallet
	./demo.py poliblogs gensim
	./demo.py poliblogs stm
	./demo.py fomc mallet
	./demo.py fomc gensim
	./demo.py fomc stm
	./demo.py 20newsgroups mallet
	./demo.py 20newsgroups gensim
	./demo.py nsfgrants mallet

################################################################################
# Other utilities

utils: utils/mallet/CorpusWriter.jar utils/corenlp/SentenceSplitter.jar

utils/mallet/CorpusWriter.jar:
	$(MAKE) -C utils/mallet

utils/corenlp/SentenceSplitter.jar:
	$(MAKE) -C utils/corenlp

################################################################################

clean:
	rm -rf externals
	rm -rf tools
