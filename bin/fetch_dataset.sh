#!/bin/bash

if [ $# -lt 1 ]
then
	echo "Usage: $0 dataset"
	exit -1
fi

DEMO=$1
DOWNLOAD_PATH=data/demo/$DEMO/download
CORPUS_PATH=data/demo/$DEMO/corpus

if [ ! -d "$CORPUS_PATH" ]
then
	echo "# Setting up the $DEMO dataset..."
	echo "    Creating folder 'data/demo/$DEMO'..."
	mkdir -p data
	mkdir -p data/demo
	mkdir -p data/demo/$DEMO

	if [ ! -e "data/demo/$DEMO/safe-to-delete.txt" ]
	then
		echo "After a model is imported into a Termite Data Server, you can delete all content in this folder without affecting the server." > data/demo/$DEMO/safe-to-delete.txt
	fi

	if [ ! -d "$DOWNLOAD_PATH" ]
	then
		mkdir -p $DOWNLOAD_PATH
		echo "    Downloading..."
		curl --insecure --location http://homes.cs.washington.edu/~jcchuang/termite-datasets/$DEMO.zip > $DOWNLOAD_PATH/$DEMO.zip
	fi

	mkdir -p $CORPUS_PATH
	echo "    Uncompressing..."
	unzip -q $DOWNLOAD_PATH/$DEMO.zip -d $CORPUS_PATH

	echo "    Corpus available: $CORPUS_PATH"
	echo
fi
