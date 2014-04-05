#!/usr/bin/env python

HYPER_PARAMS = u"""DEFAULT_ 0.01
NL_ 0.01
ML_ 100
CL_ 0.00000000001
"""

GENERATE_VOCAB_COMMANDS = u"""java -Xmx8g -cp {TOOL}/class:{TOOL}/lib/* cc.mallet.topics.tui.GenerateVocab \\
	--input {filenameMallet} \\
	--vocab {filenameVocab}"""

INIT_BASH_SCRIPT = u"""#!/bin/bash

echo ">> Generating correlations..."
java -Xmx8g -cp {TOOL}/class:{TOOL}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {filenameVocab} \\
	--constraint {filenameConstraints} \\
	--tree {filenameWN} \\
	--merge-constraints false

echo ">> Start training a topic model..."
java -Xmx8g -cp {TOOL}/class:{TOOL}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {filenameMallet} \\
	--output-interval {finalIter} \\
	--output-dir {filenameNextModel} \\
	--vocab {filenameVocab} \\
	--tree {filenameWN} \\
	--tree-hyperparameters {filenameHyperparams} \\
	--inferencer-filename {filenameInferencer} \\
	--alpha 0.5 \\
	--num-topics {numTopics} \\
	--num-iterations {finalIter} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume false \\
	--constraint {filenameConstraints} \\
	--remove-words {filenameRemoveTermsPrefix} \\
	--keep {filenameKeepTerms}
"""

RESUME_BASH_SCRIPT = u"""#!/bin/bash

echo ">> Generating correlations..."
java -Xmx8g -cp {TOOL}/class:{TOOL}/lib/* cc.mallet.topics.tui.GenerateTree \\
	--vocab {filenameVocab} \\
	--constraint {filenameConstraints} \\
	--tree {filenameWN} \\
	--merge-constraints false

echo ">> Resume training a topic model..."
java -Xmx8g -cp {TOOL}/class:{TOOL}/lib/* cc.mallet.topics.tui.Vectors2TreeTopics \\
	--input {filenameMallet} \\
	--output-interval {finalIter} \\
	--output-dir {filenameNextModel} \\
	--vocab {filenameVocab} \\
	--tree {filenameWN} \\
	--tree-hyperparameters {filenameHyperparams} \\
	--inferencer-filename {filenameInferencer} \\
	--alpha 0.5 \\
	--num-topics {numTopics} \\
	--num-iterations {finalIter} \\
	--num-top-words 480 \\
	--random-seed 0 \\
	--forget-topics doc \\
	--resume true \\
	--resume-dir {filenamePrevModel} \\
	--constraint {filenameConstraints} \\
	--remove-words {filenameRemoveTermsPrefix} \\
	--keep {filenameKeepTerms}
"""
