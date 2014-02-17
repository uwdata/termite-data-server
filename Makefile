DEMO_PATH = data/itm

all: web2py tools/mallet tools/treetm apps/infovis_mallet apps/10newsgroups apps/15newsgroups apps/20newsgroups

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

$(DEMO_PATH)/corpus: web2py tools/mallet
	mkdir -p data
	mkdir -p data/itm
	bin/fetch_20newsgroups.sh $(DEMO_PATH)

$(DEMO_PATH)/10newsgroups: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/10newsgroups 10

apps/10newsgroups: $(DEMO_PATH)/10newsgroups
	bin/import_mallet.py 10newsgroups $(DEMO_PATH)/10newsgroups
	bin/import_corpus.py 10newsgroups --terms $(DEMO_PATH)/10newsgroups/corpus.mallet

$(DEMO_PATH)/15newsgroups: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/15newsgroups 15

apps/15newsgroups: $(DEMO_PATH)/15newsgroups
	bin/import_mallet.py 15newsgroups $(DEMO_PATH)/15newsgroups
	cp -r apps/10newsgroups/data/corpus apps/15newsgroups/data/corpus

$(DEMO_PATH)/20newsgroups: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/20newsgroups 20

apps/20newsgroups: $(DEMO_PATH)/20newsgroups
	bin/import_mallet.py 20newsgroups $(DEMO_PATH)/20newsgroups
	cp -r apps/10newsgroups/data/corpus apps/20newsgroups/data/corpus

clean:
	rm -rf externals
	rm -rf web2py
	rm -rf tools/mallet*
	rm -rf tools/treetm*
	rm -rf data/demo/infovis apps/infovis_mallet
	rm -rf $(DEMO_PATH)
