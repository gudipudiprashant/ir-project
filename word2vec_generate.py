import copy
import json
import nltk
import os
import time

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models import Word2Vec

lemmatizer = WordNetLemmatizer()


def is_number(num_string):
  try:
    int(num_string)
    return True
  except ValueError:
    return False

def processSegment(segment, stop_words):
  tempSegment = word_tokenize(segment)
  # tempSegment = pattern.sub(" ", segment)
  # tempSegment = tempSegment.split()
  tempSegment = [word for word in tempSegment if not word in stop_words]
  return tempSegment


def get_clean_sentences(content):
  sentence_list = sent_tokenize(content)
  # Removing noisy sentences
  temp_list = []
  for sent in sentence_list:
    if len(sent) > 2:
      temp_list.append(sent)
  return temp_list

baseDir = "E:\College\IR\Entity"
jsonDir = "tagged_dataset"

jsonFiles = os.listdir(os.path.join(baseDir, jsonDir))

stop_words = set([])

test_ctr = 0
test_sz = 700

sent_ent_list = []
st_tagger = StanfordNERTagger(os.path.join(baseDir,
        'stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'),
                            os.path.join(baseDir,
                            'stanford-ner/stanford-ner.jar'))
all_sent_tokens_list = []

for file in jsonFiles:
  if test_sz != -1 and test_ctr >= test_sz:
    break
  test_ctr += 1

  json_dict = json.load(open(os.path.join(baseDir, jsonDir, file)))
  content = json_dict["content"]

  sentence_list = get_clean_sentences(content)

  # STanford
  all_sent_tokens_list += [processSegment(sent,
              stop_words) for sent in sentence_list]


units = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
  ]

tens = [ "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

scales = ["hundred", "thousand", "million", "lakh", ]
nums = set(units+tens+scales)


sent_ent_list = st_tagger.tag_sents(all_sent_tokens_list)

stop_words = set(stopwords.words('english'))
stop_words.union(set(["a", "an", "the"]))


for i,sent in enumerate(sent_ent_list):
  pos_tagged = nltk.pos_tag(all_sent_tokens_list[i])
  # print(pos_tagged)
  # input()
  temp_list = []
  j = 0
  while (j < len(sent)):
    joined_ent = sent[j][0]
    ent_typ = sent[j][1]
    while (j+1 < len(sent) and sent[j+1][1] != "O"
      and sent[j+1][1] == ent_typ):
      joined_ent += " " + sent[j+1][0]
      j += 1

    # lemmatize:
    if not " " in joined_ent:
      if pos_tagged[j][1].startswith("V"):
        joined_ent = lemmatizer.lemmatize(joined_ent, pos="v")
      if pos_tagged[j][1].startswith("N"):
        joined_ent = lemmatizer.lemmatize(joined_ent)

    j += 1

    if (joined_ent != "." and joined_ent != ","
      and joined_ent not in stop_words
      and joined_ent.lower() not in nums
      and not is_number(joined_ent)):
      temp_list.append(joined_ent.lower())
  sent_ent_list[i] = (temp_list)

# print(sent_ent_list)
# input()

print ("STARTING WORD2VEC")
model = Word2Vec(sent_ent_list, size=45, min_count=5, workers=7)
model.save("word2vec")

