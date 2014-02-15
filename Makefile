all: web2py mallet apps/infovis_mallet

web2py:
	bin/setup_web2py.sh

mallet tools/mallet:
	bin/setup_mallet.sh

gensim tools/gensim:
	bin/setup_gensim.sh

stmt tools/stmt:
	bin/setup_stmt.sh

apps/infovis_mallet: web2py tools/mallet
	./demo.sh infovis mallet

clean:
	rm -r externals/
	rm -r tools/
	rm -r web2py/
	rm -r data/demo/infovis apps/infovis_mallet
