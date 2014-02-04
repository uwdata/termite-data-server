DEMO_PATH = itm-data

all: $(DEMO_PATH)/10newsgroups_mallet $(DEMO_PATH)/15newsgroups_mallet $(DEMO_PATH)/20newsgroups_mallet
	./start_server.sh

setup:
	bin/setup_web2py.sh
	bin/setup_mallet.sh
	bin/setup_treetm.sh

$(DEMO_PATH)/corpus: setup
	bin/fetch_20newsgroups.sh $(DEMO_PATH)

$(DEMO_PATH)/10newsgroups_mallet: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/10newsgroups_mallet 10
	bin/import_mallet.py 10newsgroups $(DEMO_PATH)/10newsgroups_mallet
	bin/import_corpus.py 10newsgroups --terms $(DEMO_PATH)/10newsgroups_mallet/corpus.mallet

$(DEMO_PATH)/15newsgroups_mallet: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/15newsgroups_mallet 15
	bin/import_mallet.py 15newsgroups $(DEMO_PATH)/15newsgroups_mallet
	bin/import_corpus.py 15newsgroups --terms $(DEMO_PATH)/15newsgroups_mallet/corpus.mallet

$(DEMO_PATH)/20newsgroups_mallet: $(DEMO_PATH)/corpus
	bin/train_mallet.sh $(DEMO_PATH)/corpus $(DEMO_PATH)/20newsgroups_mallet 20
	bin/import_mallet.py 20newsgroups $(DEMO_PATH)/20newsgroups_mallet
	bin/import_corpus.py 20newsgroups --terms $(DEMO_PATH)/20newsgroups_mallet/corpus.mallet

clean:
	rm -rf $(DEMO_PATH)
