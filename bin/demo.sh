#!/bin/bash

DEMO_PATH=demo-20newsgroups

function __create_folder__ {
	FOLDER=$1
	TAB=$2
	if [ ! -d $FOLDER ]
	then
		echo "${TAB}Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

function __demo__ {
	__create_folder__ $DEMO_PATH
	DOWNLOAD_PATH=$DEMO_PATH/download
	CORPUS_PATH=$DEMO_PATH/corpus
	MODEL_PATH=$DEMO_PATH/model
	if [ ! -d "$DOWNLOAD_PATH" ]
	then
		echo ">> Downloading the 20newsgroups dataset..."
		__create_folder__ $DOWNLOAD_PATH "    "
		curl --insecure --location http://qwone.com/~jason/20Newsgroups/20news-18828.tar.gz > $DOWNLOAD_PATH/20news-18828.tar.gz
		echo ">> Setting up redirect to 20newsgroups information page..."
		echo "<html><head><meta http-equiv='refresh' content='0;url=http://qwone.com/~jason/20Newsgroups/'></head></html>" > $DOWNLOAD_PATH/index.html
	else
		echo ">> Downloading the 20newsgroups dataset..."
		echo "    Already downloaded: $DOWNLOAD_PATH"
	fi
	
	if [ ! -d "$CORPUS_PATH" ]
	then
		echo ">> Uncompressing the 20newsgroups dataset..."
		__create_folder__ $CORPUS_PATH "    "
		tar -zxf $DOWNLOAD_PATH/20news-18828.tar.gz 20news-18828 &&\
			mv 20news-18828/* $CORPUS_PATH &&\
			rmdir 20news-18828
	else
		echo ">> Uncompressing the 20newsgroups dataset..."
		echo "    Already uncompressed: $CORPUS_PATH"
	fi
	
	bin/import_folder.sh $CORPUS_PATH $MODEL_PATH 20newsgroups
}

bin/setup.sh
__demo__
bin/run_server.sh
