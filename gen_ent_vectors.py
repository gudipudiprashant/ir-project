# Average word2vec
# 1.
import math
import pickle
import os
import time

import numpy as np

import config
import java_handler

print("Importing Word2Vec.")
from gensim.models import Word2Vec

from Entity_test import run_ner_coref, get_relev_entities, \
get_clean_sentences, join_entities

model = Word2Vec.load("word2vec")

radius = 5

vec_dim = config.word2vec_dim

pickle_file = config.vec_pickle_file
# use as model.wv[word]

relev_category_map = {"ORGANIZATION":"ORG", "LOCATION":"LOC", "PERSON":"PER"}

def get_entity_vector(sent, ent_pos, flag = False):
  forw_vec, back_vec = [], []
  forw_centr, back_centr = np.zeros((vec_dim,)), np.zeros((vec_dim,))
  # backward
  seen = 0
  j = ent_pos - 1
  while j > 0 and sent[j][0] != "." and seen < radius:
    if sent[j][1] != "O":
      vec_word = sent[j][1]
    else:
      vec_word = sent[j][0]
    if vec_word in model.wv:
      seen += 1
      # print(vec_word)
      back_centr += model.wv[vec_word]
      back_vec.append(model.wv[vec_word])
    j -= 1
  # forward
  # print("Forward-------------")
  seen = 0
  j = ent_pos + 1
  while j < len(sent) and sent[j][0] != "." and seen < radius:
    if sent[j][1] != "O":
      vec_word = sent[j][1]
    else:
      vec_word = sent[j][0]
    if vec_word in model.wv:
      seen += 1
      # print(vec_word)
      forw_centr += model.wv[vec_word]
      forw_vec.append(model.wv[vec_word])
    j += 1

  # Normalize
  temp_ = np.dot(back_centr, back_centr)
  if temp_ != 0:
    back_centr = back_centr/(math.sqrt(temp_))

  temp_ = np.dot(forw_centr, forw_centr)
  if temp_ != 0:
    forw_centr = forw_centr/(math.sqrt(temp_))

  if flag:
    return ((back_vec, back_centr), (forw_vec, forw_centr))
  else:
    return (back_centr, forw_centr)

def generate_entity_vectors():
  baseDir = config.base_dir
  # json_dir = config.train_dataset_folder
  json_dir = config.train_dataset_folder
  json_dir = os.path.join(baseDir, json_dir)
  jsonFiles = os.listdir(json_dir)
  jsonFiles = jsonFiles
  json_dict_list = run_ner_coref(json_dir, jsonFiles)

  relev_vectors = {"LOC" : [], "PER" : [], "ORG" : []}
  non_relev_vectors = {"LOC" : [], "PER" : [], "ORG" : []}

  print("Starting...")
  t1 = time.time()
  ctr = 0
  for file, json_dict in json_dict_list:
    ctr += 1
    print(ctr)
    sentence_list_old, sent_ent_list, coref_chain_list = \
      java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))

    sentence_list, sent_ent_list = get_clean_sentences(sentence_list_old,
                sent_ent_list)
    # joins parts of the same entity
    join_entities(sent_ent_list)

    # get relev and non relev entity vectors from each file
    relev_entities = get_relev_entities(json_dict)
    all_relev = set()
    for ent_typ in relev_entities:
      all_relev.update(relev_entities[ent_typ])

    # get the vector for each entity
    for sent in sent_ent_list:
      # print(sent)
      for i, elem in enumerate(sent):
        if sent[i][1] in relev_category_map.values():
          v_b, v_f = get_entity_vector(sent, i)
          # print(np.dot(v_b, v_b))
          # print(elem)
          if sent[i][0] in all_relev:
            # print(v_b, "\n")
            # print(v_f, "\n\n")
            # print("-----------relevant---------------")
            relev_vectors[sent[i][1]].append((v_b, v_f))
          else:
            non_relev_vectors[sent[i][1]].append((v_b, v_f))
  # store the generated vecttors
  pickle.dump( [relev_vectors, non_relev_vectors], open(pickle_file, "wb"))
  print("Time taken for whole process: ", time.time() - t1)

if __name__ == "__main__":
  generate_entity_vectors()