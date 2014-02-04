#!/bin/bash

DEMO_PATH=demo-infovis
CORPUS_PATH=$DEMO_PATH/corpus
MALLET_PATH=$DEMO_PATH/model-mallet
MALLET_APP=infovis_mallet
TREETM_PATH=$DEMO_PATH/model-treetm
TREETM_APP=infovis_treetm
TREETM_PATH=$DEMO_PATH/model-stmt
TREETM_APP=infovis_stmt
GENSIM_PATH=$DEMO_PATH/model-gensim
GENSIM_APP=infovis_gensim

function __fetch_data__ {
	bin/fetch_infovis.sh $DEMO_PATH
}

function __train_mallet__ {
	echo "# Training a MALLET LDA topic model..."
	echo
	echo "bin/train_mallet.sh $CORPUS_PATH/infovis-papers.txt $MALLET_PATH"
	echo
	bin/train_mallet.sh $CORPUS_PATH/infovis-papers.txt $MALLET_PATH
	echo
}

function __import_mallet__ {
	echo "# Importing a MALLET LDA topic model..."
	echo
	echo "bin/import_mallet.py $MALLET_APP $MALLET_PATH"
	echo
	bin/import_mallet.py $MALLET_APP $MALLET_PATH
	echo
	echo "bin/import_corpus.py $MALLET_APP --meta $CORPUS_PATH/infovis-papers-meta.txt --terms $MALLET_PATH/corpus.mallet"
	echo
	bin/import_corpus.py $MALLET_APP --meta $CORPUS_PATH/infovis-papers-meta.txt --terms $MALLET_PATH/corpus.mallet
	echo
}

function __train_treetm__ {
	echo "# Training a TreeTM model..."
	echo
	echo "bin/train_treetm.py $CORPUS_PATH/infovis-papers.txt $TREETM_PATH --iters 100"
	echo
	bin/train_treetm.py $CORPUS_PATH/infovis-papers.txt $TREETM_PATH --iters 100
	echo
}

function __import_treetm__ {
	echo "# Importing a TreeTM model..."
	echo
	echo "bin/import_treetm.py $TREETM_PATH $TREETM_APP"
	echo
	bin/import_treetm.py $TREETM_PATH $TREETM_APP
	echo
	echo "bin/import_corpus.py $TREETM_APP --meta $CORPUS_PATH/infovis-papers-meta.txt --terms $MALLET_PATH/corpus.mallet"
	echo
	bin/import_corpus.py $TREETM_APP --meta $CORPUS_PATH/infovis-papers-meta.txt --terms $MALLET_PATH/corpus.mallet
	echo
}

function __train_stmt__ {
	echo "# Training a STMT model..."
	echo
	echo "bin/train_stmt.py $CORPUS_PATH/infovis-papers.txt $STMT_PATH --iters 100"
	echo
	bin/train_stmt.py $CORPUS_PATH/infovis-papers.txt $STMT_PATH --iters 100
	echo
}

function __import_stmt__ {
	echo "# Importing a STMT model..."
	echo
	echo "bin/import_stmt.py $STMT_PATH $STMT_APP"
	echo
	bin/import_stmt.py $STMT_PATH $STMT_APP
	echo
	echo "bin/import_corpus.py $STMT_APP --meta $CORPUS_PATH/infovis-papers-meta.txt"
	echo
	bin/import_corpus.py $STMT_APP --meta $CORPUS_PATH/infovis-papers-meta.txt
	echo
}

function __train_gensim__ {
	echo "# Training a gensim LDA topic model..."
	echo
	echo "bin/train_gensim.py $CORPUS_PATH/infovis-papers.txt $GENSIM_PATH"
	echo
	bin/train_gensim.py $CORPUS_PATH/infovis-papers.txt $GENSIM_PATH
	echo
}
function __import_gensim__ {
	echo "# Importing a gensim LDA topic model..."
	echo
	echo "bin/import_gensim.py $GENSIM_APP $GENSIM_PATH/corpus.dict $GENSIM_PATH/output.model"
	echo
	bin/import_gensim.py $GENSIM_APP $GENSIM_PATH/corpus.dict $GENSIM_PATH/output.model
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
	bin/setup_web2py.sh
	bin/setup_mallet.sh
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
elif [ "$MODEL" == "stmt" ] || [ "$MODEL" == "all" ]
then
	bin/setup_web2py.sh
	bin/setup_stmt.sh
	__fetch_data__
	__train_stmt__
	__import_stmt__
elif [ "$MODEL" == "gensim" ] || [ "$MODEL" == "all" ]
then
	bin/setup_web2py.sh
	bin/setup_gensim.sh
	__fetch_data__
	__train_gensim__
	__import_gensim__
fi
./start_server.sh
