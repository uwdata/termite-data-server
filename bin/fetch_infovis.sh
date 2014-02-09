#!/bin/bash

DEMO_PATH=$1
DOWNLOAD_PATH=$DEMO_PATH/download
CORPUS_PATH=$DEMO_PATH/corpus

function __create_folder__ {
	FOLDER=$1
	TAB=$2
	if [ ! -d $FOLDER ]
	then
		echo "${TAB}Creating folder: $FOLDER"
		mkdir $FOLDER
	fi
}

echo "# Setting up the infovis dataset..."
__create_folder__ $DEMO_PATH "    "

if [ ! -e "$DEMO_PATH/questionable-to-delete.txt" ]
then
	echo "After a model is imported into a Termite server, you can technically delete all content in this folder without affecting the server. However you may wish to retain these files to track provenance and for other analysis purposes." > $DEMO_PATH/questionable-to-delete.txt
fi

if [ ! -d "$DOWNLOAD_PATH" ]
then
	__create_folder__ $DOWNLOAD_PATH "    "
	echo "    Downloading..."
	curl --insecure --location http://homes.cs.washington.edu/~jcchuang/misc/files/infovis-papers.zip > $DOWNLOAD_PATH/infovis-papers.zip
else
	echo "    Already downloaded: $DOWNLOAD_PATH"
fi

if [ ! -d "$CORPUS_PATH" ]
then
	__create_folder__ $CORPUS_PATH "    "
	echo "    Uncompressing..."
	unzip $DOWNLOAD_PATH/infovis-papers.zip -d $CORPUS_PATH &&\
	    mv $CORPUS_PATH/infovis-papers/* $CORPUS_PATH &&\
	    rmdir $CORPUS_PATH/infovis-papers
else
	echo "    Already available: $CORPUS_PATH"
fi

echo
