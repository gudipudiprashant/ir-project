# Average word2vec
# 1.
import os

import numpy as np

import config
import java_handler


from gensim.models import Word2Vec
from nltk.stem import WordNetLemmatizer

from Entity_test import run_ner_coref, get_relev_entities, get_clean_sentences

lemmatizer = WordNetLemmatizer()
model = Word2Vec.load("word2vec")
radius = 5
vec_dim = 40
# use as model.wv[word]

relev_category_map = {"ORGANIZATION":"ORG", "LOCATION":"LOC", "PERSON":"PER"}

def join_entities(sent_ent_list):
  
  for i, sent in enumerate(sent_ent_list):
    temp_list = []
    j = 0
    while (j < len(sent)):
      joined_ent = sent[j][0]
      ent_typ = sent[j][1]
      # join parts of the same entity
      while (j+1 < len(sent) and sent[j+1][1] != "O"
        and sent[j+1][1] == ent_typ):
        joined_ent += " " + sent[j+1][0]
        j += 1
      joined_ent = joined_ent.lower()
      j += 1
      # add entity and it's type
      if ent_typ == "O":
        joined_ent = lemmatizer.lemmatize(joined_ent)
        joined_ent = lemmatizer.lemmatize(joined_ent, pos="v")
      if ent_typ in relev_category_map:
        ent_typ = relev_category_map[ent_typ]
      temp_list.append((joined_ent, ent_typ))

    sent_ent_list[i] = temp_list
  # print(sent_ent_list)

def get_entity_vectors(sent_ent_list, json_dict):
  relev_entities = get_relev_entities(json_dict)
  all_relev = set()
  for ent_typ in relev_entities:
    all_relev.update(relev_entities[ent_typ])
  
  relev_vectors = []
  non_relev_vectors = []
  # tagging entities as relev and non-relv
  for sent in sent_ent_list:
    # print(sent)
    for i, elem in enumerate(sent):
      if sent[i][1] in relev_category_map.values():
        # print(elem)
        # Is normalization neccessary
        vec = np.zeros((vec_dim,))
        # backward
        seen = 0
        j = i - 1
        while j > 0 and sent[j][0] != "." and seen < radius:
          if sent[j][1] != "O":
            vec_word = sent[j][1]
          else:
            vec_word = sent[j][0]
          if vec_word in model.wv:
            seen += 1
            # print(vec_word)
            vec += model.wv[vec_word]
          j -= 1
        # forward
        # print("Forward-------------")
        seen = 0
        j = i + 1
        while j < len(sent) and sent[j][0] != "." and seen < radius:
          if sent[j][1] != "O":
            vec_word = sent[j][1]
          else:
            vec_word = sent[j][0]
          if vec_word in model.wv:
            seen += 1
            # print(vec_word)
            vec += model.wv[vec_word]
          j += 1
        # add vector to corresponding category
        if sent[i][0] in all_relev:
          # print(elem)
          relev_vectors.append(vec)
        else:
          non_relev_vectors.append(vec)
    # break
          # sent[i] = (sent[i][0], sent[i][1], "R")
  return relev_vectors, non_relev_vectors

def generate_entity_vectors():
  baseDir = config.base_dir
  # json_dir = config.train_dataset_folder
  json_dir = config.test_dataset_folder
  json_dir = os.path.join(baseDir, json_dir)
  jsonFiles = os.listdir(json_dir)
  jsonFiles = jsonFiles[:1]
  json_dict_list = run_ner_coref(json_dir, jsonFiles)

  relev_vectors, non_relev_vectors = [], []

  for file, json_dict in json_dict_list:
    sentence_list_old, sent_ent_list, coref_chain_list = \
      java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))

    sentence_list, sent_ent_list = get_clean_sentences(sentence_list_old,
                sent_ent_list)
    # joins parts of the same entity
    join_entities(sent_ent_list)

    # get relev and non relev entity vectors from each file
    v1, v2 = get_entity_vectors(sent_ent_list, json_dict)
    relev_vectors += v1
    non_relev_vectors += v2
    print(relev_vectors, non_relev_vectors)

if __name__ == "__main__":
  generate_entity_vectors()