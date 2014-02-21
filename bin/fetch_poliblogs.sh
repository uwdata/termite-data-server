#!/bin/bash

if [ $# -ge 1 ]
then
	DEMO_PATH=$1
else
	DEMO_PATH=demo-poliblogs
fi
DOWNLOAD_PATH=$DEMO_PATH/download
CORPUS_PATH=$DEMO_PATH/corpus

function __create_folder__ {
	FOLDER=$1
	if [ ! -d $FOLDER ]
	then
		echo "    Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

echo "# Setting up the poliblogs2008 dataset..."
__create_folder__ $DEMO_PATH

if [ ! -e "$DEMO_PATH/questionable-to-delete.txt" ]
then
	echo "After a model is imported into a Termite server, you can technically delete all content in this folder without affecting the server. However you may wish to retain these files to track provenance and for other analysis purposes." > $DEMO_PATH/questionable-to-delete.txt
fi

if [ ! -d "$DOWNLOAD_PATH" ]
then
	__create_folder__ $DOWNLOAD_PATH
	echo "    Downloading..."
	curl --insecure --location http://homes.cs.washington.edu/~jcchuang/misc/files/poliblogs2008.csv.zip > $DOWNLOAD_PATH/poliblogs2008.csv.zip
	curl --insecure --location http://homes.cs.washington.edu/~jcchuang/misc/files/poliblogs2008.RData.zip > $DOWNLOAD_PATH/poliblogs2008.RData.zip
else
	echo "    Already downloaded: $DOWNLOAD_PATH"
fi

if [ ! -d "$CORPUS_PATH" ]
then
	__create_folder__ $CORPUS_PATH
	echo "    Uncompressing..."
	unzip $DOWNLOAD_PATH/poliblogs2008.csv.zip -d $CORPUS_PATH
	unzip $DOWNLOAD_PATH/poliblogs2008.RData.zip -d $CORPUS_PATH
else
	echo "    Already available: $CORPUS_PATH"
fi

echo
