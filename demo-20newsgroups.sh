#!/bin/bash

DEMO_PATH=demo-20newsgroups
DOWNLOAD_PATH=$DEMO_PATH/download
CORPUS_PATH=$DEMO_PATH/corpus
MALLET_PATH=$DEMO_PATH/model-mallet
MALLET_APP=20newsgroups_mallet
TREETM_PATH=$DEMO_PATH/model-treetm
TREETM_APP=20newsgroups_treetm

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

function __train_mallet__ {
	echo "# Training a MALLET LDA topic model..."
	echo
	echo "bin/train_mallet.sh $CORPUS_PATH $MALLET_PATH"
	echo
	bin/train_mallet.sh $CORPUS_PATH $MALLET_PATH
	echo
}

function __import_mallet__ {
	echo "# Importing a MALLET LDA topic model..."
	echo
	echo "bin/ImportMallet.py $MALLET_PATH $MALLET_APP"
	echo
	bin/ImportMallet.py $MALLET_PATH $MALLET_APP
	echo
}

function __train_treetm__ {
	echo "# Training a TreeTM model..."
	echo
	echo "bin/TrainTreeTM.py $CORPUS_PATH $TREETM_PATH --iters 1000"
	echo
	bin/TrainTreeTM.py $CORPUS_PATH $TREETM_PATH --iters 1000
	echo
}

function __import_treetm__ {
	echo "# Importing a TreeTM model..."
	echo
	echo "bin/ImportTreeTM.py $TREETM_PATH $TREETM_APP"
	echo
	bin/ImportTreeTM.py $TREETM_PATH $TREETM_APP
	echo
}

if [ $# -gt 0 ]
then
	MODEL=$1
else
	MODEL=mallet
fi
if [ "$MODEL" == "mallet" ] || [ "$MODEL" == "all" ]
then
	bin/setup.sh
	__fetch_data__
	__train_mallet__
	__import_mallet__
elif [ "$MODEL" == "treetm" ] || [ "$MODEL" == "all" ]
then
	bin/setup_web2py.sh
	bin/setup_treetm.sh
	__fetch_data__
	__train_treetm__
	__import_treetm__
fi
bin/start_server.sh
