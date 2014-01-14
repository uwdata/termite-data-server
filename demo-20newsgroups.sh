#!/bin/bash

DEMO_PATH=demo-20newsgroups
DEMO_APP=20newsgroups
TREETM_APP=20newsgroups_treetm
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
	echo "# Setting up the 20newsgroups dataset..."
	__create_folder__ $DEMO_PATH "    "
	
	if [ ! -e "$DEMO_PATH/README" ]
	then
		echo "After a model is imported into a Termite server, you can technically delete all content in this folder without affecting the server. However you may wish to retain your model for other analysis purposes." > $DEMO_PATH/README
	fi

	if [ ! -d "$DOWNLOAD_PATH" ]
	then
		__create_folder__ $DOWNLOAD_PATH "    "
		echo "    Downloading the 20newsgroups dataset..."
		curl --insecure --location http://qwone.com/~jason/20Newsgroups/20news-18828.tar.gz > $DOWNLOAD_PATH/20news-18828.tar.gz
		echo "    Setting up 20newsgroups information page..."
		echo "<html><head><meta http-equiv='refresh' content='0;url=http://qwone.com/~jason/20Newsgroups/'></head></html>" > $DOWNLOAD_PATH/index.html
	else
		echo "    Already downloaded: $DOWNLOAD_PATH"
	fi
	
	if [ ! -d "$CORPUS_PATH" ]
	then
		__create_folder__ $CORPUS_PATH "    "
		echo "    Uncompressing the 20newsgroups dataset..."
		tar -zxf $DOWNLOAD_PATH/20news-18828.tar.gz 20news-18828 &&\
			mv 20news-18828/* $CORPUS_PATH &&\
			rmdir 20news-18828
	else
		echo "    Already available: $CORPUS_PATH"
	fi

	echo
}

function __train_model__ {
	echo "# Training an LDA model..."
	echo
	echo "bin/train_mallet_from_folder.sh $CORPUS_PATH $MODEL_PATH"
	echo
	bin/train_mallet_from_folder.sh $CORPUS_PATH $MODEL_PATH
}

function __import_model__ {
	echo "# Importing an LDA model..."
	echo
	echo "bin/ImportMallet.py $MODEL_PATH $DEMO_APP"
	echo
	bin/ImportMallet.py $MODEL_PATH $DEMO_APP
}

function __train_tree_model__ {
	echo "# Training a TreeTM model..."
	echo
	echo "bin/TrainTreeTM.py $CORPUS_PATH $MODEL_PATH-treetm --iters 1000"
	echo
	bin/TrainTreeTM.py $CORPUS_PATH $MODEL_PATH-treetm --iters 1000
}

function __import_tree_model__ {
	echo "# Importing a TreeTM model..."
	echo
	echo "bin/ImportTreeTM.py $MODEL_PATH-treetm $DEMO_APP_TREETM"
	echo
	bin/ImportTreeTM.py $MODEL_PATH-treetm $DEMO_APP_TREETM
}

bin/setup.sh
__fetch_data__
__train_model__
__import_model__
#__train_tree_model__
#__import_tree_model__
bin/start_server.sh
