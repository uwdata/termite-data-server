from collections import defaultdict
import re
from math import floor, log

import nltk
from nltk.corpus.reader.wordnet import information_content
from nltk.corpus.reader.wordnet import WordNetICCorpusReader
from nltk.corpus import wordnet as wn

from python_lib.wordnet_file_pb2 import *
from python_lib import flags

flags.define_string("vocab", "vocab/semcor.voc", \
                      "the vocabulary used for building the tree")
flags.define_string("hyperparam", "DEFAULT", "How to assign hyperparameters")
flags.define_int("num_hyp", 0, "Number of distinct hyperparameters")
flags.define_string("output_tree", "wn", "Where we write out tree")
flags.define_string("output_hyper", "wn", "Where we write the hyperparameter")

kEPSILON = 1e-6

class OntologyWriter:

    def __init__(self, filename, vocab=set(),
                 propagate_counts=True, max_leaves=10000):
        self.parents_ = defaultdict(set)

        # Keep track of how many output files we've written
        self.num_files_ = 0
        self.max_leaves_ = max_leaves
        self.filename_ = filename
        self.filter_words_ = vocab

        self.leaf_synsets_ = {}
        self.internal_synsets_ = {}

        self.internal_wn_ = WordNetFile()
        self.leaf_wn_ = WordNetFile()
        self.leaf_wn_.root = -1

        self.root_ = None
        self.vocab_ = defaultdict(dict)
        self.finalized_ = False
        self.propagate_counts_ = propagate_counts

    def parents(self, id):
        p = list(self.parents_[id])
        if len(p) == 0:
            if self.root_ == None:
                self.root_ = id
            assert self.root_ == id, "Both %i and %i appear to be root" \
                   % (id, self.root_)
            return []
        else:
            for ii in self.parents_[id]:
                p += self.parents(ii)
        return p

    def term_id(self, lang, term):
        if not term in self.vocab_[lang]:
            self.vocab_[lang][term] = len(self.vocab_)

        return self.vocab_[lang][term]

    def FindRoot(self, synsets):
        for ii in synsets:
            if ii % 1000 == 0:
                print "Finalizing", ii
            for pp in self.parents(ii):
                if self.propagate_counts_:
                    self.internal_synsets_[pp].hyponym_count += \
                        synsets[ii].raw_count
            assert synsets[ii].hyponym_count > 0, \
                   "Synset %s had zero hyponym" % synsets[ii].key

    def Finalize(self):
        """
        Check topology and percolate counts if that hasn't been done already.
        """
        if self.max_leaves_ > 0:
            self.FindRoot(self.leaf_synsets_)
            self.Write(self.leaf_wn_)

        self.FindRoot(self.internal_synsets_)

        assert self.root_ != None, "No root has been found"
        self.internal_wn_.root = self.root_
        self.Write(self.internal_wn_)

    def Write(self, wn_proto):
        if self.max_leaves_ > 0:
            filename = self.filename_ + ".%s" % str(self.num_files_)
        else:
            filename = self.filename_

        f = open(filename, "wb")
        s = wn_proto.SerializeToString()
        f.write(s)
        print "Serialized version ", s[:10], "(", len(s), \
              ") written to", filename
        f.close()
        self.num_files_ += 1

    def AddSynset(self, numeric_id, sense_key, children,
                  words, hyponym_count=0.0, hyperparameter="DEFAULT"):
        """
        @param numeric_id : A unique identifier of the synset (something like
        the offset)
        @param sense_key : A string identifying the synset (e.g. a current WN
        sense key)
        @param children : A list of the identifiers of the synset's children
        @param words : A list of (lang, word, count) tuples
        @param hyponym_count: The count of all the synsets beneath this synset.
        (Note that this does not include the count of the words in this
        argument; that will get added to the count for when it is stored in the
        protocol buffer)
        """

        assert not numeric_id in self.internal_synsets_, \
            "internal %i already added" % numeric_id
        assert not numeric_id in self.leaf_synsets_, \
            "leaf %i already added" % numeric_id

        if len(children) > 0 or self.max_leaves_ == -1:
            s = self.internal_wn_.synsets.add()
        else:
            s = self.leaf_wn_.synsets.add()

        s.offset = numeric_id
        s.key = sense_key

        for ii in children:
            self.parents_[ii].add(numeric_id)
            s.children_offsets.append(ii)

        for lang, term, count in words:
            if self.filter_words_ and not term in self.filter_words_:
                continue

            w = s.words.add()
            w.lang_id = lang
            w.term_id = self.term_id(lang, term)
            w.term_str = term
            w.count = count
            s.raw_count += count

        if s.raw_count == 0:
            s.raw_count = kEPSILON

        if len(children) > 0:
            self.internal_synsets_[numeric_id] = s
        else:
            self.leaf_synsets_[numeric_id] = s
        s.hyponym_count = s.raw_count + hyponym_count

        # If we have too many synsets, write them out
        if self.max_leaves_ > 0 and \
                len(self.leaf_synsets_) >= self.max_leaves_:
            self.FindRoot(self.leaf_synsets_)
            self.Write(self.leaf_wn_)
            self.leaf_wn_ = WordNetFile()
            self.leaf_wn_.root = -1
            self.leaf_synsets_ = {}
        s.hyperparameter = hyperparameter

        # print sense_key, "HYP=(%s)" % s.hyperparameter


def big_test(hyperparam, treefilename, hyperfilename, vocab, version="3.0",
             max_length=2):
    """
    @param hyperparam A function that, given a synset, returns a hyperparameter
    value

    @param version The version of WordNet we use

    @param max_length The maximum length of n-grams we'll use for computing
    counts
    """
    from python_lib.wordnet import load_wn
    from nltk.corpus import brown
    from nltk.util import ingrams

    wn = load_wn(version)

    term_counts = defaultdict(int)

    for ngram_length in xrange(max_length):
        token = 0
        for w in ingrams(brown.words(), ngram_length):
            token += 1
            normalized = "_".join(w).lower()
            if wn.synsets(normalized, 'n'):
                term_counts[wn.morphy(normalized)] += 1

    print("Done collecting counts")

    if not treefilename:
        treefilename = "wn/wordnet.wn"
        if version != "3.0":
            treefilename = "wn/wordnet_%s.wn" % version

    o = OntologyWriter(treefilename, vocab=vocab, max_leaves=-1)
    for ii in wn.all_synsets('n'):
        o.AddSynset(ii.offset,
                    ii.name,
                    [x.offset for x in ii.hyponyms() + ii.instance_hyponyms()],
                    [(0, x.name.lower(), term_counts[x.name] + 1)
                     for x in ii.lemmas], hyperparameter=hyperparam(ii))
    o.Finalize()

    #hyperparam.dump(filename + "_hyp.lookup")
    hyperparam.dump(hyperfilename)


def toy_test():
    """
    Tests the writer on a toy dataset.
    """

    #              ------- (140) 1730 -------
    #           /                              \
    #        (60)              (10)            (80)
    #        1900: ------------2001:---------  2000:
    #          |               gummy_bear (5)    |
    #          |               gummibaer (5)     |
    #          |                                 |
    #          |   animal (5)                    |   food (5)
    #         /\   tier (5)                     /\   essen (5)
    #        /  \                             /    \
    #      (10) (30)                        (40)  (20)
    #      2010 2020                        3000  3010
    #   (5) dog pig (10)               (20) pork  dog (5)
    # (3) hound schwein (20)         (5) schwein  hot dog (5)
    # (2)  hund               (15) schweinfleish  hotdog (5)
    #                                             hotdog (5)
    #  Words (German):
    #  0     essen
    #  1     tier
    #  2     hund
    #  3     schwein
    #  4     schweinfleish
    #  5     hotdog
    #  6     gummibaer
    #  Words (English):
    #  0     food
    #  1     animal
    #  2     dog
    #  3     hound
    #  4     pork
    #  5     pig
    #  6     hot dog
    #  7     hotdog
    #  8     gummy bear

    o = OntologyWriter("wn/animal_food_toy.wn")
    o.AddSynset(1730, "entity", [1900, 2000], [])
    o.AddSynset(1900, "animal", [2010, 2001, 2020],
                [(ENGLISH, "animal", 5), (GERMAN, "tier", 5)])
    o.AddSynset(2000, "food", [3000, 2001, 3010],
                [(ENGLISH, "food", 5), (GERMAN, "essen", 5)])
    o.AddSynset(2001, "gummy bear", [],
                [(ENGLISH, "gummy_bear", 5), (GERMAN, "gumibaer", 5)])
    o.AddSynset(2010, "dog", [],
                [(ENGLISH, "dog", 5), (ENGLISH, "hound", 3),
                 (GERMAN, "hund", 2)])
    o.AddSynset(2020, "pig", [],
                [(ENGLISH, "pig", 10), (GERMAN, "schwein", 20)])
    o.AddSynset(3000, "pork", [],
                [(ENGLISH, "pork", 20), (GERMAN, "schwein", 5),
                 (GERMAN, "schweinfleish", 15)])
    o.AddSynset(3010, "hot dog", [],
                [(ENGLISH, "dog", 5), (ENGLISH, "hot_dog", 5),
                 (GERMAN, "hotdog", 5), (ENGLISH, "hotdog", 5)])
    o.Finalize()


def getLanguage(flag):
    language = {
        '0': ENGLISH,
        '1': GERMAN,
        '2': CHINESE,
        '3': FRENCH,
        '4': SPANISH,
        '5': ARABIC}
    return language[flag]


def get_vocab(vocab_fn):
    vocab = set()
    for line in open(vocab_fn):
        words = line.strip()
        w = words.split('\t')
        # check whether we need to use lower case or not
        # vocab.add(w[1].lower())
        # for nih data, we cannot use lower case,
        # since there are words like "pi3" and "PI3"
        vocab.add(w[1])
    return vocab


def write_leaf(cons, current_index, leaf_count, allocated_index,
               o, constraints_count):
    current_index += 1
    wordset = []
    lang = ENGLISH
    for word in cons[1]:
        if word not in constraints_count.keys():
            num = 1.0
        else:
            num = 1.0 / constraints_count[word]
        wordset.append((lang, word, num))

    #name = cons[0] + "%s" % (":".join(cons[1][:20]))
    name = cons[0]

    hyperparameter = "DEFUALT"
    if re.search("ML_", name):
        hyperparameter = "ML_"
    elif re.search("CL_", name):
        hyperparameter = "CL_"
    elif re.search("NL_", name):
        hyperparameter = "NL_"
    elif re.search("ROOT", name):
        hyperparameter = "NL_"

    o.AddSynset(current_index, name, [], wordset,
                hyperparameter=hyperparameter)

    return current_index, leaf_count, allocated_index


def write_internal_nodes(cons, current_index, leaf_count, allocated_index,
                         o, constraints_count):

    if not (re.search('^NL_IN_$', cons[0]) or re.search('^CL_$', cons[0])):
        [current_index, leaf_count, allocated_index] = \
        write_leaf(cons, current_index, leaf_count, allocated_index, o,
                   constraints_count)
        return current_index, leaf_count, allocated_index

    current_index += 1
    name = cons[0]
    child_count = len(cons[1])
    start = allocated_index + 1
    o.AddSynset(current_index, name, xrange(start, start + child_count), [])
    allocated_index += child_count
    child_index = start - 1

    for clique in cons[1]:
        [child_index, leaf_count, allocated_index] = \
        write_internal_nodes(clique, child_index, leaf_count,
                             allocated_index, o, constraints_count)

    return current_index, leaf_count, allocated_index


class HyperparameterSelector:
    """
    Class that provides a function to select a hyperparameter for a synset
    """

    def bin(self, val):
        if self.num > 0:
            b = int(floor(float(val) / (1.01 * (self.max - self.min)) * \
                              self.num))

            assert b < self.num and b >= 0, "Had bin %i and val %f" % (b, val)
            return b
        else:
            return val

    def dump(self, file):
        o = open(file, 'w')
        #o.write("%i\n" % len(self.seen))
        for ii in self.seen:
            #o.write("%s\t1.0\t1.0\t1.0\n" % (ii))
            o.write("%s 1.0\n" % (ii))
        o.close()

    def default(self, x):
        return 0

    def depth(self, x):
        return x.max_depth()

    def unique(self, x):
        return x.offset

    def ic(self, x):
        if not self._ic:
            wnic = WordNetICCorpusReader(nltk.data.find('corpora/wordnet_ic'),
                                         '.*\.dat')
            self._ic = wnic.ic('ic-bnc-resnik-add1.dat')

        val = information_content(x, self._ic)

        return val

    def children(self, x):
        return len(self._hypo(x))

    def desc(self, x):
        return sum(1 for x in x.closure(self._hypo))

    def eval(self, x):
        val = self.func(x)

        self.min = min(val, self.min)
        self.max = max(val, self.max)

        return val

    def __call__(self, x):
        val = self.prefix + "-%i" % self.bin(self.eval(x))
        self.seen.add(val)
        return val

    def __init__(self, scheme, num=1):

        self.min = float("inf")
        self.max = float("-inf")
        self.num = num
        self.seen = set()

        self._hypo = lambda s: s.hyponyms() + s.instance_hyponyms()
        self._ic = None

        if scheme == "depth":
            self.func = self.depth
        elif scheme == "random":
            self.func = lambda x: abs(hash(x)) % 7919 # a smallish prime
        elif scheme == "children":
            self.func = self.children
        elif scheme == "ic":
            self.func = self.ic
        elif scheme == "descendants":
            self.func = self.desc
        elif scheme == "unique":
            self.func = self.unique
            self.num = 0
        else:
            scheme = "default"
            self.func = self.default
            self.num = 0

        self.prefix = "%s" % scheme.upper()

if __name__ == "__main__":
    flags.InitFlags()

    vocab = get_vocab(flags.vocab)
    hyper_sel = HyperparameterSelector(flags.hyperparam, flags.num_hyp)

    min_val = float("inf")
    for ii in wn.all_synsets('n'):
        hyper_sel.eval(ii)

    #big_test(hyper_sel, "%s/%s-%i" % (flags.output_dir,
    #                                  flags.output_filename,
    #                                  hyper_sel.num), vocab)
    big_test(hyper_sel, flags.output_tree, flags.output_hyper, vocab)
