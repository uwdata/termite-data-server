all: web2py tools/mallet apps/infovis_mallet

web2py:
	bin/setup_web2py.sh

mallet tools/mallet:
	bin/setup_mallet.sh

gensim tools/gensim:
	bin/setup_gensim.sh

stm tools/stm:
	bin/setup_stm.sh

treetm tools/treetm:
	bin/setup_treetm.sh

stmt tools/stmt:
	bin/setup_stmt.sh

apps/infovis_mallet: web2py tools/mallet
	./demo.sh infovis mallet

clean:
	rm -rf externals
	rm -rf web2py
	rm -rf tools/mallet*
	rm -rf data/demo/infovis apps/infovis_mallet
