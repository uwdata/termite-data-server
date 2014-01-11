#from topicmod.util.wordnet import load_wn
#from topicmod.util import flags
from python_lib.wordnet import load_wn
from python_lib import flags
from nltk.corpus.reader.wordnet import WordNetError
from collections import defaultdict
import codecs

pos_tags = ["n", "v", "a", "r"]

def readVocab(vocabname):
  infile = open(vocabname, 'r')
  vocab = defaultdict(dict)
  for line in infile:
    line = line.strip()
    ww = line.split('\t')
    vocab[ww[0]][ww[1]] = 1
  infile.close()
  return vocab

def generateCons(vocab, wn, outfilename, num_cons):
  lang = '0'
  cons = defaultdict(dict)
  for word in vocab[lang]:
    for pos in pos_tags:
      synsets = wn.synsets(word, pos)
      for syn in synsets:
        if not syn.offset in cons[pos]:
          cons[pos][syn.offset] = set()
        cons[pos][syn.offset].add(word)

  outfile = codecs.open(outfilename, 'w', 'utf-8')
  multipaths = defaultdict(dict)
  count = 0
  for pos in cons:
    for syn in cons[pos]:
      if len(cons[pos][syn]) > 1:
        count += 1
        if count <= num_cons or num_cons == -1:
          words = list(cons[pos][syn])
          tmp = "\t".join(words)
          outfile.write("MERGE_\t" + tmp + "\n")
          for word in words:
            if not pos in multipaths[word]:
              multipaths[word][pos] = set()
            multipaths[word][pos].add(syn)
  outfile.close()

  #outfilename = outfilename.replace(".cons", ".interested")
  #generateInterestingWords(outfilename, multipaths)


def generateInterestingWords(outfilename, multipaths):
  
  outfile = codecs.open(outfilename, 'w', 'utf-8')
  count_word = 0
  count_sense = 0
  word_senses_count = defaultdict()
  im_words = ""
  for word in multipaths:
    word_senses_count[word] = 0
    count_word += 1
    tmp = word
    for pos in multipaths[word]:
      tmp += '\t' + pos
      for index in multipaths[word][pos]:
        word_senses_count[word] += 1
        count_sense += 1
        tmp += '\t' + str(index)
    if word_senses_count[word] > 1:
      im_words += word + " "
    outfile.write(tmp + '\n')
  outfile.write("\nThe total number of cons words: " + str(count_word) + "\n")
  outfile.write("\nThe total number of cons words senses: " + str(count_sense) + "\n")
  outfile.write("\nInteresting words: " + im_words + "\n")
  outfile.close()

flags.define_string("vocab", None, "The input vocab")
flags.define_string("output", None, "The output constraint file")
flags.define_int("num_cons", -1, "The number of constraints we want")

if __name__ == "__main__":

  flags.InitFlags()
  #eng_wn = load_wn("3.0", "../../../data/wordnet/", "wn")
  eng_wn = load_wn()
  vocab = readVocab(flags.vocab)
  generateCons(vocab, eng_wn, flags.output, flags.num_cons)
