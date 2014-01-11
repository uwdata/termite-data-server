
This readme describes how to use WordNet, the lexical ontology, as the prior instead of a hand-constructed topic prior.

There are two options for how to use WordNet.  The first is to use WordNet to generate constraints (a tree of depth two), and the second is to use the entire hyponym tree of WordNet (a tree of depth seventeen).

For more information about WordNet, see:
http://wordnet.princeton.edu/

For both of these approaches, we use the interface provided by nltk.

http://nltk.org

After you've installed nltk, you also need to install the WordNet corpus (corpora/wordnet) and brown corpus (corpora/brown) to estimate the hyperparameters.

======================================
 WordNet to Generate Constraints
======================================

This script creates a set of positive correlations based on synsets in WordNet:

python scripts/extract_constraints_wordnet.py --vocab $INPUTDIR/$DATANAME.voc --output $INPUTDIR/$DATANAME.cons --num_cons -1

The number of constraints is based on the num_cons flag; If it is set to be -1, it will extract all the correlations from wordnet for your data.

======================================
 Use All of WordNet
======================================

In addition to nltk, this approach also requires you to install a protocol buffer compiler and the protocol buffer python libraries.

(1) compile the python protocol buffer
protoc --proto_path=scripts/python_lib --python_out=scripts/python_lib scripts/python_lib/wordnet_file.proto

(this places the output in the current directory; if you do not want the output to live here, it must be accessible from your $PYTHONPATH)

(2) create the WordNet protocol buffer:
python scripts/ontology_writer.py --vocab=input/synthetic.voc --output_tree=input/synthetic.all.wn --output_hyper=input/synthetic.hyper

(of course, use the vocabulary file that corresponds to your data. and Don't forget that the generate tree file name is synthetic.all.wn, use this name in the command for topic models.)


(3) At this point, you should be able to use the output (the default will be called "input/wn" for the tree and "input/wn.lookup" for the hyperparameters) as the --tree and --tree-hyperparameters arguments to the main program, Vectors2TreeTopics.

You can also generate your own arbitrary trees by encoding it as a protocol buffer.
