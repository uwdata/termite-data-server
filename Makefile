DEMO_PATH = data/itm
APPS_PATH = web2py/applications

all: web2py tools/mallet tools/treetm $(APPS_PATH)/infovis_mallet $(APPS_PATH)/10newsgroups $(APPS_PATH)/15newsgroups $(APPS_PATH)/20newsgroups

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

$(DEMO_PATH)/corpus:
	mkdir -p data
	mkdir -p data/itm
	bin/fetch_20newsgroups.sh $(DEMO_PATH)

$(DEMO_PATH)/10newsgroups: $(DEMO_PATH)/corpus tools/mallet
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/10newsgroups 10

$(APPS_PATH)/10newsgroups: $(DEMO_PATH)/10newsgroups web2py
	bin/import_mallet.py 10newsgroups $(DEMO_PATH)/10newsgroups
	bin/import_corpus.py 10newsgroups --terms $(DEMO_PATH)/10newsgroups/corpus.mallet

$(DEMO_PATH)/15newsgroups: $(DEMO_PATH)/corpus tools/mallet
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/15newsgroups 15

$(APPS_PATH)/15newsgroups: $(DEMO_PATH)/15newsgroups web2py
	bin/import_mallet.py 15newsgroups $(DEMO_PATH)/15newsgroups
	cp -r apps/10newsgroups/data/corpus apps/15newsgroups/data/corpus

$(DEMO_PATH)/20newsgroups: $(DEMO_PATH)/corpus tools/mallet
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/20newsgroups 20

$(APPS_PATH)/20newsgroups: $(DEMO_PATH)/20newsgroups web2py
	bin/import_mallet.py 20newsgroups $(DEMO_PATH)/20newsgroups
	cp -r apps/10newsgroups/data/corpus apps/20newsgroups/data/corpus

clean:
	rm -rf externals
	rm -rf web2py
	rm -rf tools/mallet*
	rm -rf tools/treetm*
	rm -rf data/demo/infovis apps/infovis_mallet
	rm -rf $(DEMO_PATH)
	rm -rf apps/10newsgroups
	rm -rf apps/15newsgroups
	rm -rf apps/20newsgroups
