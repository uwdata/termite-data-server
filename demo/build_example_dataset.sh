#!/bin/bash

EXTERNALS_PATH=externals
CORPUS_PATH=corpus
MODELS_PATH=models
DATA_PATH=data

function __create_folder__ {
	FOLDER=$1
	if [ ! -d $FOLDER ]
	then
		echo "Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __download_data__ {
	EXTERNALS_SUBPATH=$EXTERNALS_PATH/20newsgroups
	CORPUS_SUBPATH=$CORPUS_PATH/20newsgroups
	if [ ! -d "$CORPUS_SUBPATH" ]
	then
		__create_folder__ $CORPUS_SUBPATH
		__create_folder__ $EXTERNALS_SUBPATH

		echo ">> Downloading the 20newsgroups dataset..."
		curl --insecure --location http://qwone.com/~jason/20Newsgroups/20news-18828.tar.gz > $EXTERNALS_SUBPATH/20news-18828.tar.gz
		
		echo ">> Uncompressing the 20newsgroups dataset..."
		tar -zxvf $EXTERNALS_SUBPATH/20news-18828.tar.gz 20news-18828 &&\
			mv 20news-18828/* $CORPUS_SUBPATH &&\
			rmdir 20news-18828
		
		echo ">> Setting up redirect to 20newsgroups information page..."
		echo "<html><head><meta http-equiv='refresh' content='0;url=http://qwone.com/~jason/20Newsgroups/'></head></html>" > $EXTERNALS_SUBPATH/index.html
	else
		echo ">> Downloading the 20newsgroups dataset..."
		echo "    Folder already exists: $CORPUS_SUBPATH"
	fi
}

function __build_model__ {
	CORPUS_SUBPATH=$CORPUS_PATH/20newsgroups
	MODELS_SUBPATH=$MODELS_PATH/20newsgroups
	DATA_SUBPATH=$DATA_PATH/20newsgroups
	bin/import_folder.sh $CORPUS_SUBPATH $MODELS_SUBPATH $DATA_SUBPATH
}

bin/setup.sh
__create_folder__ $CORPUS_PATH
__create_folder__ $MODELS_PATH
__create_folder__ $DATA_PATH
__download_data__
__build_model__
