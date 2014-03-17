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

tools/mallet mallet:
	bin/setup_mallet.sh

tools/gensim gensim:
	bin/setup_gensim.sh

tools/stm stm:
	bin/setup_stm.sh

tools/treetm treetm:
	bin/setup_treetm.sh

tools/stmt stmt:
	bin/setup_stmt.sh

################################################################################
# Demos
#   Download and build an LDA model using the InfoVis dataset

demo: web2py tools/mallet
	./demo.sh infovis mallet

################################################################################

clean:
	rm -rf externals
	rm -rf web2py
	rm -rf tools/mallet*
	rm -rf data/demo/infovis apps/infovis_mallet web2py/applications/infovis_mallet
