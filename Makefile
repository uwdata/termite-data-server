all: web2py infovis

web2py:
	bin/setup_web2py.sh

tools/mallet:
	bin/setup_mallet.sh

tools/gensim:
	bin/setup_gensim.sh

tools/stmt:
	bin/setup_stmt.sh

infovis apps/infovis_mallet: web2py tools/mallet
	./demo.sh infovis mallet

20newsgroups apps/20newsgroups_mallet: web2py tools/mallet
	./demo.sh 20newsgroups mallet

gensim apps/infovis_gensim: web2py tools/gensim
	./demo.sh infovis gensim

stmt apps/infovis_stmt: web2py tools/stmt
	./demo.sh infovis stmt

clean:
	rm -r externals/
	rm -r tools/
	rm -r web2py/
	rm -r apps/infovis_mallet
