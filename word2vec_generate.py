import os
import time

import nltk

import config
import java_handler
from gensim.models import Word2Vec

from Entity_test import run_ner_coref, get_relev_entities, get_clean_sentences
from gen_ent_vectors import join_entities


def gen_word2vec():

  stopwords = set(["-lrb-", "-rrb-", ";", ":", "'s", "a", "an", "the",
  "(", ")", ".", ",", "=", "-", "'", "`", "and"])
  
  baseDir = config.base_dir
  jsonDir = config.test_dataset_folder
  print(jsonDir)
  # changing jsondir
  jsonDir = os.path.join(baseDir, jsonDir)
  print(jsonDir)
  jsonFiles = os.listdir(os.path.join(jsonDir))

  json_dict_list = run_ner_coref(jsonDir, jsonFiles)
  # to store all the sentences for word2vec generation
  all_sent_list = []
  
  t1 = time.time()
  for file, json_dict in json_dict_list:
    sentence_list_old, sent_ent_list, coref_chain_list = \
      java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))

    _, sent_ent_list = get_clean_sentences(sentence_list_old,
                sent_ent_list)
    # joins parts of the same entity
    join_entities(sent_ent_list)
    # print("SENT ENT LIST:", sent_ent_list)
    #
    for sent in (sent_ent_list):
      temp_list = []
      for ii, elem in enumerate(sent):
        if elem[1] != "O":
          temp_list.append(elem[1])
        elif elem[0] not in stopwords:
          temp_list.append(elem[0])

      all_sent_list.append(temp_list)

  # print("\n\n")
  # print("ALL ENT LIST: " ,all_sent_list)
  print("Time taken to pre-process: ", time.time() - t1)
  print ("STARTING WORD2VEC")
  model = Word2Vec(all_sent_list, size=40, min_count=5, workers=7)
  model.save("word2vec")


if __name__ == "__main__":
  gen_word2vec()