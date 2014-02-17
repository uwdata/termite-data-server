DEMO_PATH = data/itm

all: web2py tools/mallet $(DEMO_PATH)/10newsgroups $(DEMO_PATH)/15newsgroups $(DEMO_PATH)/20newsgroups

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

$(DEMO_PATH)/corpus: web2py tools/mallet
	mkdir -p data
	mkdir -p data/itm
	bin/fetch_20newsgroups.sh $(DEMO_PATH)

$(DEMO_PATH)/10newsgroups: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/10newsgroups 10
	bin/import_mallet.py 10newsgroups $(DEMO_PATH)/10newsgroups
	bin/import_corpus.py 10newsgroups --terms $(DEMO_PATH)/10newsgroups/corpus.mallet

$(DEMO_PATH)/15newsgroups: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/15newsgroups 15
	bin/import_mallet.py 15newsgroups $(DEMO_PATH)/15newsgroups
	cp -r apps/10newsgroups/data/corpus apps/15newsgroups/data/corpus

$(DEMO_PATH)/20newsgroups: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/20newsgroups 20
	bin/import_mallet.py 20newsgroups $(DEMO_PATH)/20newsgroups
	cp -r apps/10newsgroups/data/corpus apps/20newsgroups/data/corpus

clean:
	rm -r $(DEMO_PATH)
	rm -r externals web2py tools/mallet* data/demo/infovis apps/infovis_mallet
