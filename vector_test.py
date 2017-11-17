# entity vector ranker
import math
import pickle
import time

import numpy as np

import config

from Entity_test import Tester, join_entities
from gen_ent_vectors import get_entity_vector

# contains two dictionaries - one for relevant vector and
# other for non-relevant
ent_vectors = pickle.load(open(config.vec_pickle_file, "rb"))  


def custom_score(v1_b, v1_f, v2_b, v2_f):
  return max(np.dot(v1_b, v2_b), np.dot(v1_f, v2_f))

def kNN(ent_vec_back, ent_vec_forw, k, ent_typ):
  # contains two tuples - class and score
  all_sim = []
  for i in range(2):
    ctr = 0
    for vec_b, vec_f in ent_vectors[i][ent_typ]:
      # ctr += 1
      # if ctr > 10:
      #   break
      score = custom_score(vec_b, vec_f, ent_vec_back, ent_vec_forw)
      all_sim.append((score, i))

  all_sim = sorted(all_sim, reverse=True)
  # print(all_sim[:10])
  categ = [0,0]
  for i in range(k):
    categ[all_sim[i][1]] += 1
  # print(categ)
  return categ.index(max(categ))


centroid_vec = [{"PER": None, "ORG" : None, "LOC": None},
                {"PER": None, "ORG" : None, "LOC": None}]

def centroid_similarity(ent_vec_back, ent_vec_forw, ent_typ):
  if centroid_vec[0]["PER"] is None:
    print("Only once")
    calc_centroid()

  scores = []
  for i in range(2):
    scores.append( custom_score(ent_vec_back, ent_vec_forw, 
      centroid_vec[i][ent_typ][0], centroid_vec[i][ent_typ][1]) )

  return scores.index(max(scores))

def calc_centroid():
  # put check on whether centroid has to be calculated at func call
  for i in range(2):
    for ent_typ in centroid_vec[0].keys():
      if len(ent_vectors[i][ent_typ]) == 0:
        print("Err.. problem!", ent_typ, "centroid calculation")
        input()
      # both forward and backward centroid
      vecs = []
      for j in range(2):
        vec = np.zeros((config.word2vec_dim,))
        for elem in ent_vectors[i][ent_typ]:
          vec += elem[j]
        temp_ = np.dot(vec, vec)
        if temp_ != 0:
          centroid_vec[i][ent_typ] = vec/math.sqrt(temp_)
        else:
          centroid_vec[i][ent_typ] = vec
    
        vecs.append(vec)

      centroid_vec[i][ent_typ] = vecs 

def custom_entity_detect_func(sent_ent_list, sentence_list, content,
  custom_param):
  # print("Inside")
  # t1 = time.time()
  join_entities(sent_ent_list)
  relev_entities = {
                  "LOC": [],
                  "ORG": [],
                  "PER": [],
                  }

  # k_ = custom_param.get("kNN", 3)

  # get the vector for each entity
  for sent in sent_ent_list:
    # print(sent)
    for i, _ in enumerate(sent):
      if sent[i][1] in relev_entities.keys():
        # print(sent[i])
        ent_vec_back, ent_vec_forw = get_entity_vector(sent, i)
        # various methods - possible - kNN or centroid or ...
        # if kNN(ent_vec_back, ent_vec_forw, k_, sent[i][1]) == 0:
        if centroid_similarity(ent_vec_back, ent_vec_forw, sent[i][1]) == 0:  
          # print("Relevant\n")
          relev_entities[sent[i][1]].append(sent[i][0])

  # print(time.time()-t1)
  return relev_entities


def main():
  tester = Tester(custom_entity_detect_func, size=-1, stop=False,)
  tester.test()
  tester.score(True)

if __name__ == "__main__":
  main()
