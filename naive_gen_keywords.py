# Extracting keywords
import json
import os
import pickle
import time

import config

from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


lemmatizer = WordNetLemmatizer()
# Word tokenize json number mismatch
mismatch = 5

stop_words = set(stopwords.words('english'))
# corpus specific
stop_words = stop_words.union(set(["-lrb-", "-rrb-", "(", ")",
  ",", "a", "an", "the", "said", "'s"]))

# HACK
close_words_glob = None


def get_json_relev_entities(json_dict):
  json_format = {
      "LOC"   : "Event",
      "ORG"   : "Accused",
      "PER"   : "Accused",
  }

  relev_entities = {
      "LOC"   :   [],
      "ORG"   :   [],
      "PER"   :   [],
    }
  for ent_type in json_format.keys():
    for ent in json_dict[ent_type]:
      if ent[2] == json_format[ent_type]:
        # convert to lower
        try:
          relev_entities[ent_type].append((ent[0].strip().lower(), int(ent[1])))
        except Exception as e:
          print ("Error: ", e)
          # Value Error -
          pass
  return relev_entities

def valid_keyword(word, relev_entities):
  if word not in stop_words:
    ent_flag = False
    for typ in relev_entities.keys():
      # ---------- TO DO ----------
      # Not good enough - normal english words like liberation 
      # will also get removed - i need to send more info
      for ent, _ in relev_entities[typ]:
        if word in ent:
          ent_flag = True
    if not ent_flag:
      return True
  return False

def get_close_words(tokenized_string, relev_entities, close_words,
  radius=4):

  for ent_type in close_words.keys():
    for ent, pos in relev_entities[ent_type]:
      # determine the exact position in the tokenized string
      for start_pos_str in range(pos - mismatch, pos + mismatch):
        if ent.startswith(tokenized_string[start_pos_str]):
          break

      for end_pos_str in range(start_pos_str, start_pos_str+10):
        if ent.endswith(tokenized_string[end_pos_str]):
          break
      
      # add the words before pos_str and after pos_sr
      seen = 0
      i = start_pos_str - 1
      while (seen < radius and i >= 0):
        if tokenized_string[i] in [".", ":"]:
          break
        elif valid_keyword(tokenized_string[i], relev_entities):
          lem_word = lemmatizer.lemmatize(tokenized_string[i], "v")
          close_words[ent_type][lem_word] += 1
          seen += 1
        i -= 1

      seen = 0
      i = end_pos_str + 1
      while (seen < radius and i < len(tokenized_string)):
        if tokenized_string[i] in [".", ":"]:
          break
        elif valid_keyword(tokenized_string[i], relev_entities):
          lem_word = lemmatizer.lemmatize(tokenized_string[i], "v")
          close_words[ent_type][lem_word] += 1
          seen += 1
        i += 1

  return close_words

# Current things in param:
# radius - radius of important words around relev entity
# threshold - number of close words to be returned after sorting
# sub_common - removes the close words common to both relev and
# non-relev entities
def gen_keywords(param):
  print ("ONLY ONCE")
  global close_words_glob

  if hasattr(config, "base_dir"):
    base_dir = config.base_dir

  threshold = param.get("threshold", 10)
  radius = param.get("radius", 4)

  base_dir = "E:\College\IR\Entity"
  if close_words_glob is not None:
    return close_words_glob

  print ("ONLY ONCE")
  jsonDir = "tagged_dataset"
  jsonFiles = os.listdir(os.path.join(base_dir, jsonDir))

  close_words = { 
      "LOC"   :   Counter(),
      "ORG"   :   Counter(),
      "PER"   :   Counter(),
    }

  for file in jsonFiles:
    json_dict = json.load(open(os.path.join(base_dir, jsonDir, file)))
    # get the content
    content = json_dict["content"]
    relev_entities = get_json_relev_entities(json_dict)
    # tokenize content
    tokenized_string = word_tokenize(content)
    tokenized_string = [word.lower() for word in tokenized_string]

    get_close_words(tokenized_string, relev_entities, close_words, 
      radius)

  
  for ent_type in close_words.keys():
    print (ent_type)
    temp_list = [(close_words[ent_type][word], word) for \
        word in close_words[ent_type].keys()]
    temp_list = sorted(temp_list, reverse=True)

    close_words[ent_type] = [elem[1] for elem in temp_list[:threshold]]

  close_words_glob = close_words
  return close_words

if __name__ == "__main__":
  gen_keywords()
# Convert tokenized string to lower

