import os
import pickle
import time

import config
import java_handler

from collections import Counter

from nltk.util import ngrams

from config import relev_category_map
from Entity_test import join_entities, get_clean_sentences, run_ner_coref\
, get_relev_entities
import kneser

stopwords = set(["-lrb-", "-rrb-", ";", ":", "'s", "a", "an", "the",
  "(", ")", ".", ",", "=", "-", "'", "`", "and", "his", "which"])

# entity is relev/non relev:
# (w1, w2, REL/NONREL)
# (w2, REL?NON, w3)
# (REL/NOn, w3, w4)

def get_ngram_phrase(sent, pos, rel_tag):
  n = config.n_
  # pad words in phrase
  phrase = []
  for i in range(pos-n+1, pos+n):
    if i < 0:
      phrase.append("<s>")
    elif i >= len(sent):
      phrase.append("</s>")
      break
    else:
      if i == pos:
        phrase.append(rel_tag)
      elif sent[i][1] != "O":
        phrase.append(sent[i][1])
      else:
        phrase.append(sent[i][0])

  return phrase

def train_ngram():
  n = config.n_
  baseDir = config.base_dir
  # json_dir = config.train_dataset_folder
  json_dir = config.train_dataset_folder
  json_dir = os.path.join(baseDir, json_dir)
  jsonFiles = os.listdir(json_dir)
  json_dict_list = run_ner_coref(json_dir, jsonFiles)

  all_grams = {i+1:[] for i in range(n)}
  print(all_grams)

  print("Starting...")
  t1 = time.time()
  ctr = 0

  for file, json_dict in json_dict_list:
    # ctr += 1
    # print(ctr)
    sentence_list_old, sent_ent_list, coref_chain_list = \
      java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))

    sentence_list, sent_ent_list = get_clean_sentences(sentence_list_old,
                sent_ent_list)
    # joins parts of the same entity
    join_entities(sent_ent_list)
    # get relev entities
    relev_entities = get_relev_entities(json_dict)
    # print(relev_entities)

    for sent in sent_ent_list:
      # remove stopwords
      temp_list = []
      for i in range(len(sent)):
        if sent[i][0] not in stopwords:
          temp_list.append(sent[i])
      sent = temp_list

      for i, elem in enumerate(sent):
        if elem[1] in relev_entities.keys():
          rel_tag = ""

          if elem[0] in relev_entities[elem[1]]:
            rel_tag = "REL"
          else:
            rel_tag = "NONREL"
          phrase = get_ngram_phrase(sent, i, rel_tag)
          for i in range(1, n+1):
            i_grams = ngrams(phrase, i)
            temp_grams = [x for x in i_grams]
            # print(temp_grams)
            all_grams[i] += temp_grams
          # print(temp_)
  # calculate counts and probability for each n gram
  for i in range(1, n+1):
    all_grams[i] = Counter(all_grams[i])
    # tot = sum(all_grams[i].values())
    # print("For ",i, ": ", tot, len(all_grams[i].keys()))
    # for elem in all_grams[i]:
    #   all_grams[i][elem] = all_grams[i][elem]/tot

  # print(len(vocab))
  # print(len(all_grams))
  pickle.dump(all_grams, open(config.ngram_pickle_file, "wb"))
  print(" Time taken: ", time.time() - t1)
  return all_grams


if __name__ == "__main__":
  train_ngram()