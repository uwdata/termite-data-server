#!/bin/bash

DEMO_PATH=demo-infovis
NEWSGROUP_APP=infovis
TREETM_APP=infovis_treetm
DOWNLOAD_PATH=$DEMO_PATH/download
CORPUS_PATH=$DEMO_PATH/corpus
MODEL_PATH=$DEMO_PATH/model

function __create_folder__ {
	FOLDER=$1
	TAB=$2
	if [ ! -d $FOLDER ]
	then
		echo "${TAB}Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __fetch_data__ {
	echo "# Setting up the infovis dataset..."
	__create_folder__ $DEMO_PATH "    "
	
	if [ ! -e "$DEMO_PATH/README" ]
	then
		echo "After a model is imported into a Termite server, you can technically delete all content in this folder without affecting the server. However you may wish to retain your model for other analysis purposes." > $DEMO_PATH/README
	fi

	if [ ! -d "$DOWNLOAD_PATH" ]
	then
		__create_folder__ $DOWNLOAD_PATH "    "
		echo "    Downloading the infovis dataset..."
		curl --insecure --location http://homes.cs.washington.edu/~jcchuang/misc/files/infovis-papers.zip > $DOWNLOAD_PATH/infovis-papers.zip
	else
		echo "    Already downloaded: $DOWNLOAD_PATH"
	fi
	
	if [ ! -d "$CORPUS_PATH" ]
	then
		__create_folder__ $CORPUS_PATH "    "
		echo "    Uncompressing the infovis dataset..."
		unzip $DOWNLOAD_PATH/infovis-papers.zip -d $CORPUS_PATH &&\
		    mv $CORPUS_PATH/infovis-papers/* $CORPUS_PATH &&\
		    rmdir $CORPUS_PATH/infovis-papers
	else
		echo "    Already available: $CORPUS_PATH"
	fi

	echo
}

function __train_mallet_model__ {
	echo "# Training a MALLET LDA model..."
	echo
	echo "bin/train_mallet.sh $CORPUS_PATH/infovis-papers.txt $MODEL_PATH"
	echo
	bin/train_mallet.sh $CORPUS_PATH/infovis-papers.txt $MODEL_PATH
}

function __import_mallet_model__ {
	echo "# Importing a MALLET LDA model..."
	echo
	echo "bin/ImportMallet.py $MODEL_PATH $NEWSGROUP_APP"
	echo
	bin/ImportMallet.py $MODEL_PATH $NEWSGROUP_APP
	echo
	echo "bin/ImportCorpus.py $NEWSGROUP_APP $CORPUS_PATH/infovis-papers-meta.txt"
	echo
	bin/ImportCorpus.py $NEWSGROUP_APP $CORPUS_PATH/infovis-papers-meta.txt
	echo
}

function __train_tree_model__ {
	echo "# Training a TreeTM model..."
	echo
	echo "bin/TrainTreeTM.py $CORPUS_PATH/infovis-papers.txt $MODEL_PATH-treetm --iters 50 --is_file"
	echo
	bin/TrainTreeTM.py $CORPUS_PATH/infovis-papers.txt $MODEL_PATH-treetm --iters 50 --is_file
}

function __import_tree_model__ {
	echo "# Importing a TreeTM model..."
	echo
	echo "bin/ImportTreeTM.py $MODEL_PATH-treetm $TREETM_APP"
	echo
	bin/ImportTreeTM.py $MODEL_PATH-treetm $TREETM_APP
	echo
	echo "bin/ImportCorpus.py $TREETM_APP $CORPUS_PATH/infovis-papers-meta.txt"
	echo
	bin/ImportCorpus.py $TREETM_APP $CORPUS_PATH/infovis-papers-meta.txt
	echo
}

bin/setup.sh
__fetch_data__
__train_mallet_model__
__import_mallet_model__
__train_tree_model__
__import_tree_model__
bin/start_server.sh
