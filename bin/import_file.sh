#!/bin/bash

if [ $# -lt 3 ]
then
	echo "Usage: `basename $0` corpus_filename model_folder app_identifier"
	echo
	exit -1
fi

APPS_PATH=apps

CORPUS_FILENAME=$1
MODEL_FOLDER=$2
APP_IDENTIFIER=$3
MALLET_ROOT=tools/mallet-2.0.7
WEB2PY_ROOT=tools/web2py
WEB2PY_REL=../..
NUM_TOPICS=20
NUM_ITERS=1000

if [ ! -d "$MODEL_FOLDER" ]
then
	mkdir $MODEL_FOLDER
	echo ">> Importing corpus into Mallet: [$CORPUS_FILENAME] --> [$MODEL_FOLDER/corpus.mallet]"
	$MALLET_ROOT/bin/mallet import-file \
		--input $CORPUS_FILENAME \
		--output $MODEL_FOLDER/corpus.mallet \
		--remove-stopwords \
		--token-regex "\p{Alpha}{3,}" \
		--keep-sequence

	echo ">> Building a topic model: [$NUM_TOPICS topics]"
	$MALLET_ROOT/bin/mallet train-topics \
		--input $MODEL_FOLDER/corpus.mallet \
		--output-model $MODEL_FOLDER/output.model \
		--output-topic-keys $MODEL_FOLDER/output-topic-keys.txt \
		--topic-word-weights-file $MODEL_FOLDER/topic-word-weights.txt \
		--word-topic-counts-file $MODEL_FOLDER/word-topic-counts.txt \
		--num-topics $NUM_TOPICS \
		--num-iterations $NUM_ITERS
else
	echo ">> Building a topic model: [$CORPUS_FOLDER] --> [$MODEL_FOLDER]"
	echo "    Already exists: $MODEL_FOLDER"
fi

if [ ! -d "$APPS_PATH/$APP_IDENTIFIER" ]
then
	echo ">> Creating app folder: [$APPS_PATH/$APP_IDENTIFIER]"
	echo "mkdir $APPS_PATH/$APP_IDENTIFIER"
	mkdir $APPS_PATH/$APP_IDENTIFIER
fi

if [ ! -d "$APPS_PATH/$APP_IDENTIFIER/data" ]
then
	echo ">> Preparing app data: [$MODEL_FOLDER] --> [$APPS_PATH/$APP_IDENTIFIER/data]"
	bin/ReadMallet.py $MODEL_FOLDER $APPS_PATH/$APP_IDENTIFIER/data
fi

if [ ! -e "$APPS_PATH/$APP_IDENTIFIER/controllers" ]
then
	echo ">> Setting up app controllers: [$APPS_PATH/$APP_IDENTIFIER/controllers]"
	echo "ln -s ../../server_src/controllers $APPS_PATH/$APP_IDENTIFIER/controllers"
	ln -s ../../server_src/controllers $APPS_PATH/$APP_IDENTIFIER/controllers
fi

if [ ! -e "$WEB2PY_ROOT/applications/$APP_IDENTIFIER" ]
then
	echo ">> Setting up app on web2py server: [$APP_IDENTIFIER]"
	echo "ln -s $WEB2PY_REL/../$APPS_PATH/$APP_IDENTIFIER $WEB2PY_ROOT/applications/$APP_IDENTIFIER"
	ln -s $WEB2PY_REL/../$APPS_PATH/$APP_IDENTIFIER $WEB2PY_ROOT/applications/$APP_IDENTIFIER
fi
