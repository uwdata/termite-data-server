#!/bin/bash

if [ $# -lt 3 ]
then
	echo "Usage: `basename $0` corpus_folder model_folder data_folder"
	echo
	exit -1
fi

CORPUS_FOLDER=$1
MODEL_FOLDER=$2
DATA_FOLDER=$3
MALLET_ROOT=tools/mallet-2.0.7
MALLET_FILENAME=$MODEL_FOLDER/corpus.mallet
NUM_TOPICS=20
NUM_ITERS=20

if [ ! -d "$MODEL_FOLDER" ]
then
	echo ">> Importing corpus into Mallet: [$CORPUS_FOLDER] --> [$MALLET_FILENAME]"
	$MALLET_ROOT/bin/mallet import-dir \
		--input $CORPUS_FOLDER \
		--output $MALLET_FILENAME \
		--remove-stopwords \
		--token-regex "\p{Alpha}{3,}" \
		--keep-sequence

	echo ">> Building a topic model: [$NUM_TOPICS topics]"
	$MALLET_ROOT/bin/mallet train-topics \
		--input $MALLET_FILENAME \
		--output-model $MODEL_FOLDER/output.model \
		--output-topic-keys $MODEL_FOLDER/output-topic-keys.txt \
		--topic-word-weights-file $MODEL_FOLDER/topic-word-weights.txt \
		--word-topic-counts-file $MODEL_FOLDER/word-topic-counts.txt \
		--num-topics $NUM_TOPICS \
		--num-iterations $NUM_ITERS
else
	echo ">> Building a topic model: [$CORPUS_FOLDER] --> [$MODEL_FOLDER]"
	echo "    Model already exists: $MODEL_FOLDER"
fi

if [ ! -d "$DATA_FOLDER" ]
then
	echo ">> Extracting topic model outputs: [$MODEL_FOLDER] --> [$DATA_FOLDER]"
	bin/ReadMallet.py $MODEL_FOLDER $DATA_FOLDER
else
	echo ">> Extracting topic model outputs: [$MODEL_FOLDER] --> [$DATA_FOLDER]"
	echo "    Data already exists: $DATA_FOLDER"
fi
