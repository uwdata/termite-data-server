all: web2py tools/mallet apps/infovis_mallet

web2py:
	bin/setup_web2py.sh

tools/mallet:
	bin/setup_mallet.sh

tools/gensim:
	bin/setup_gensim.sh

tools/stm:
	bin/setup_stm.sh

tools/treetm:
	bin/setup_treetm.sh

tools/stmt:
	bin/setup_stmt.sh

apps/infovis_mallet: web2py tools/mallet
	./demo.sh infovis mallet

data/poliblogs:
	mkdir -p data
	mkdir -p data/poliblogs
	bin/fetch_poliblogs.sh data/poliblogs

poliblogs apps/poliblogs_stm: web2py tools/stm data/poliblogs
	bin/import_stm.py poliblogs_stm data/poliblogs/corpus/poliblogs2008.RData
	bin/import_corpus.py poliblogs_stm --csv data/poliblogs/corpus/poliblogs2008.csv

clean:
	rm -rf externals
	rm -rf web2py
	rm -rf tools/mallet*
	rm -rf data/demo/infovis apps/infovis_mallet web2py/applications/infovis_mallet
