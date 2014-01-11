"""
Utility functions for dealing with NLTK's WordNet reader.

Author: Jordan Boyd-Graber
"""

import os

import nltk
from nltk.corpus.reader.wordnet import WordNetCorpusReader
from nltk.corpus.reader.wordnet import WordNetICCorpusReader
from nltk.data import find

def key_clean(key):
    key = key.strip()
    if key[-1] != ':':
        key = key.replace("%3", "%5")
    return key

def load_ic(file = "ic-brown-resnik-add1.dat"):
    ic_reader = WordNetICCorpusReader(find("corpora/wordnet_ic/"), file)
    ic = ic_reader.ic(file)
    return ic

def closure(s, op, visited = set([])):
    current = s
    for ii in op(s):
        if ii not in visited:
            visited.add(ii)
            closure(ii, op, visited)
    return visited

def load_wn(version="3.0", location="../../data/wordnet/", base="wn"):
    """
    I kept forgetting how to load WordNet, and this makes it easier to handle
    different versions of wordnet.  Assumes that in the nltk_data directory a
    directory called "alt_wordnets" exists, and the dict directory of every
    version is named "base-0.0" (e.g. "wn-1.6") inside that directory.

    Returns an initialized wn reader.  Defaults to the normal installation if
    it can't find the WN you're looking for (pay attention to the error
    message if that happens, as you might not be using the version you
    thought).
    """
    path = location + "%s-%s" % (base, version)
    print "Looking for ", path
    if os.path.exists(path):
        return WordNetCorpusReader(path)
    else:
        print("Failed to find WN - defaulting to NLTK's version")
        return WordNetCorpusReader(nltk.data.find("corpora/wordnet"))
