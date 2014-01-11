This file walks through the process for creating a corpus and ontology for
tree-based topic modeling.

The model created here is based on research that attempts to combine knowledge repositories and topic modelings:

* Jordan Boyd-Graber, David M. Blei, and Xiaojin Zhu. A Topic Model for Word
  Sense Disambiguation. Empirical Methods in Natural Language Processing, 2007.

* Yuening Hu, Jordan Boyd-Graber, and Brianna Satinoff. Interactive Topic
  Modeling. Association for Computational Linguistics, 2011.

* Yuening Hu and Jordan Boyd-Graber. Efficient Tree-Based Topic
  Modeling. Association for Computational Linguistics, 2012.

Please direct questions about this code to Yuening Hu, ynhu@cs.umd.edu

=== Prerequisites ===

You only need java to run this package (we have only tested this with Sun Java,
however).

If you want to look at the tree structure, you should also install the command
line tools that come with protocol buffers.  This is the serialization format
that we use to encode the knowledge repositories:

https://code.google.com/p/protobuf/

If you want to use the correlations from wordnet, also make sure you installed
python and nltk, and corpora/wordnet in nltk.

=== Compiling the code ===

(0) cd tree-TM folder and define,

DATANAME=synthetic
DATASOURCE=../../../data/synthetic/segmented
INPUTDIR=input
OUTPUTDIR=output
TESTDATA=synthetic-test
TESTSOURCE=../../../data/synthetic/test

* Notice: replace DATASOURCE and TESTSOURCE with your own directory for data, these two are only used in step (2), and in this synthetic example, we don't need to run step (2) so don't need these two variable.

(1) Compile src code
mkdir class
javac -cp class:lib/* src/cc/mallet/topics/*/*.java -d class

=== Preparing the Data ===

This example assumes you have a set of documents, one per file, stored in a
directory.  For more information in importing data into Mallet:
http://mallet.cs.umass.edu/import.php

(2) Read each documents and save in mallet input format (training and testing data):
bin/mallet import-dir --input $DATASOURCE --output $INPUTDIR/$DATANAME-topic-input.mallet --keep-sequence

bin/mallet import-dir --input $TESTSOURCE --output $INPUTDIR/$TESTDATA-topic-input.mallet --keep-sequence

* Notice: this step is to import the training data and test data to mallet input format. You don't need to run this step in this synthetic example, use it when you want to use your own data. Also, you can add --remove-stopwords option if you want. But for synthetic data, not necessary.

(3) Generate vocab file after mallet preprocessing:
java -cp class:lib/* cc.mallet.topics.tui.GenerateVocab --input $INPUTDIR/$DATANAME-topic-input.mallet --tfidf-thresh 1 --freq-thresh 1 --word-length 2 --tfidf-rank true --vocab $INPUTDIR/$DATANAME.voc

* Notice: you can filter out the vocal by --freq-thresh, --tfidf-thresh, --word-length, also, you can rank the vocab by tfidf via --tfidf-rank (default ranking by frequency)

(4) Generate trees:

(4.1) Generate correlations: you can either define your own correlations:
following the format in input/example.cons to specify your own correlations.  Or
you can extract correlations from wordnet (see wordnet_readme.txt for details).

(4.2) Generating a tree encoding correlations:
java -cp class:lib/* cc.mallet.topics.tui.GenerateTree --vocab $INPUTDIR/$DATANAME.voc --constraint $INPUTDIR/$DATANAME.cons --merge-constraints true --tree $OUTPUTDIR/$DATANAME.wn

* Notice: The correlation file can be empty (or simply do not use --constraints
option), then it is just a tree with symmetric prior, working as the normal LDA.
If you set merge-constraints as true, if you want to merge A and B, and merge B
and C and set merge-constraints as true, the new constraint will be merge A, B
and C.

* If you want to check the generated tree structure:
cat output/synthetic.wn.0 | protoc lib/proto/wordnet_file.proto --decode=topicmod_projects_ldawn.WordNetFile --proto_path=lib/proto/ > tmp0.txt
cat output/synthetic.wn.1 | protoc lib/proto/wordnet_file.proto --decode=topicmod_projects_ldawn.WordNetFile --proto_path=lib/proto/ > tmp1.txt

=== Running Inference ===

(5) Train tree topic models:

java -cp class:lib/* cc.mallet.topics.tui.Vectors2TreeTopics --input $INPUTDIR/$DATANAME-topic-input.mallet --output-dir $OUTPUTDIR/model --tree $OUTPUTDIR/$DATANAME.wn --tree-hyperparameters input/tree_hyperparams --vocab $INPUTDIR/$DATANAME.voc --alpha 0.5 --output-interval 50 --num-topics 5 --num-iterations 300 --random-seed 0

* Notice: you can check the results in the output folder. Check the model.lhood for model likelihood; check model.topics for top words of each topic; check model.states for topic assignment and path assignment of each token (each line is a document), and the format is "topic:path" for a token; check model.docs for the topic distribution of each document (each line is a document).

* Notice: if you want to map the path to the tree structure, first use the way in step (4) "cat..." to create the readable tree structure, check each path of a word, and from left to right, each path is indexed as 0,1,2...


(6) Resume tree topic models:

* Resume for running more iterations in step (5):
java -cp class:lib/* cc.mallet.topics.tui.Vectors2TreeTopics --input $INPUTDIR/$DATANAME-topic-input.mallet --output-dir $OUTPUTDIR/model --tree $OUTPUTDIR/$DATANAME.wn --tree-hyperparameters input/tree_hyperparams --vocab $INPUTDIR/$DATANAME.voc --alpha 0.5 --random-seed 0 --output-interval 10 --num-topics 5 --num-iterations 500 --resume true --resume-dir $OUTPUTDIR/model

* Notice: using the same parameters as in the step (5), except using more --num-iterations.

* Resume with a different tree:
first generate the tree as in step (4): $OUTPUTDIR/$DATANAME-new.wn
java -cp class:lib/* cc.mallet.topics.tui.Vectors2TreeTopics --input $INPUTDIR/$DATANAME-topic-input.mallet --output-dir $OUTPUTDIR/model --tree $OUTPUTDIR/$DATANAME-new.wn --tree-hyperparameters input/tree_hyperparams --vocab $INPUTDIR/$DATANAME.voc --alpha 0.5 --random-seed 0 --output-interval 10 --num-topics 5 --num-iterations 500 --resume true --resume-dir $OUTPUTDIR/model --remove-words $OUTPUTDIR/removed --forget-topics doc --constraint $OUTPUTDIR/$DATANAME.cons

* Notice: using the same parameters as in the step (5), except using more --num-iterations.
          this step is for interactive topic modeling, and supports you to run more iterations with new constraints.
          once you have new constraints, you need to generate your new tree, and then resume.
          the option --forget-topics specifies the way to forget the topic assignment of constraint words or documents containing constraint words.
          you can use --keep to keep the topic assignments of a list of words if you don't want to change the topic.
          you can use --remove-words to specify a list of words which users want to remove during the interaction.

(7) Inference on test documents:
specify the inferencer in step (5), --inferencer-filename $OUTPUTDIR/inferencer

java -cp class:lib/* cc.mallet.topics.tui.InferTreeTopics --input $INPUTDIR/$TESTDATA-topic-input.mallet --inferencer $OUTPUTDIR/inferencer --output-doc-topics $OUTPUTDIR/test.topics --random-seed 0 --num-iterations 100

=== Evaluation ===

(8) Evaluation:
specify the evaluator on step (5), --evaluator-filename $OUTPUTDIR/evaluator

java -cp class:lib/* cc.mallet.topics.tui.EvaluateTreeTopics --input $INPUTDIR/$TESTDATA-topic-input.mallet --evaluator $OUTPUTDIR/evaluator --output-doc-probs $OUTPUTDIR/test.doc-probs --output-prob $OUTPUTDIR/test.prob --num-particles 10 --use-resampling true --random-seed 0

*** Notice ***

This implementation of tree-based topic modeling is following the framework of mallet package.
The code can be easily merged to mallet by:
* move "cc.mallet.topics.tree" folder to the mallet src folder cc.mallet.topics
* merge "Verctor2TopicsTTM.java" with the one with in mallet (cc.mallet.topics.tui.Vector2Topics.java)? (Not sure we want to merge or not)
* adding new lib file: wordnet.jar
