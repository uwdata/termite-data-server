#!/bin/bash

DEMO_PATH=demo-infovis
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

function __train_model__ {
	echo "# Training an LDA mode..."
	echo
	echo "bin/TrainTreeTM.py $CORPUS_PATH/papers.txt $MODEL_PATH --is_file"
	echo
	bin/TrainTreeTM.py $CORPUS_PATH/papers.txt $MODEL_PATH --is_file
}

function __import_model__ {
	echo "# Importing an LDA model..."
	echo
	echo "bin/import_mallet.sh $MODEL_PATH infovis"
	echo
	bin/import_mallet.sh $MODEL_PATH infovis
}

bin/setup.sh
__train_model__
__import_model__
bin/start_server.sh
