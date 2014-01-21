#!/bin/bash

if [ $# -lt 2 ]
then
	echo "Usage: `basename $0` corpus_path model_folder"
	echo
	exit -1
fi

CORPUS_PATH=$1
MODEL_FOLDER=$2
MALLET_ROOT=tools/mallet-2.0.7
NUM_TOPICS=20
NUM_ITERS=1000

echo "# Building a topic model: [$CORPUS_PATH] --> [$MODEL_FOLDER]"

if [ ! -d "$MODEL_FOLDER" ]
then
	mkdir $MODEL_FOLDER
	
	if [ -d $CORPUS_PATH ]
	then
		echo "    Importing a folder into Mallet: [$CORPUS_PATH] --> [$MODEL_FOLDER/corpus.mallet]"
		$MALLET_ROOT/bin/mallet import-dir \
			--input $CORPUS_PATH \
			--output $MODEL_FOLDER/corpus.mallet \
			--remove-stopwords \
			--token-regex "\p{Alpha}{3,}" \
			--keep-sequence
	elif [ -f $CORPUS_PATH ]
	then
		echo "    Importing a file into Mallet: [$CORPUS_PATH] --> [$MODEL_FOLDER/corpus.mallet]"
		$MALLET_ROOT/bin/mallet import-file \
			--input $CORPUS_PATH \
			--output $MODEL_FOLDER/corpus.mallet \
			--remove-stopwords \
			--token-regex "\p{Alpha}{3,}" \
			--keep-sequence
	fi

	echo "    Training an LDA model: [$NUM_TOPICS topics, $NUM_ITERS iterations]"
	$MALLET_ROOT/bin/mallet train-topics \
		--input $MODEL_FOLDER/corpus.mallet \
		--output-model $MODEL_FOLDER/output.model \
		--output-topic-keys $MODEL_FOLDER/output-topic-keys.txt \
		--topic-word-weights-file $MODEL_FOLDER/topic-word-weights.txt \
		--output-doc-topics $MODEL_FOLDER/doc-topic-mixtures.txt \
		--word-topic-counts-file $MODEL_FOLDER/word-topic-counts.txt \
		--num-topics $NUM_TOPICS \
		--num-iterations $NUM_ITERS
else
	echo "    Already exists: $MODEL_FOLDER"
fi

echo
