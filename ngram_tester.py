import pickle
import time


import config

from Entity_test import join_entities, Tester
from kneser import KneserNeyLM
from ngram_generate import get_ngram_phrase

all_ngrams = pickle.load(open(config.ngram_pickle_file, "rb"))
# lm = KneserNeyLM(config.n_, all_ngrams)

def prob(phrase, pos, n):
  if n == 1:
    c2 = sum(all_ngrams[n].values())
  else:
    c2 = all_ngrams[n-1].get(tuple(phrase[pos-n+1 : pos]), 0)
  c1 = all_ngrams[n].get(tuple(phrase[pos-n+1 : pos+1]), 0)
  if c1 > 0:
    return c1/c2
  return 0

def stupid_backoff_score(phrase):
  n = config.n_
  score = 1
  for i in range(n-1, len(phrase)):
    prob_i = 1
    k = n
    while k > 0 and prob(phrase, i, k) == 0:
      prob_i *= 0.4
      k -= 1

    prob_i *= prob(phrase, i, k)
  score *= prob_i
  # print(phrase,score)
  return score



def custom_entity_detect_func(sent_ent_list, sentence_list, content,
  custom_param):
  # print("Inside")
  #DEBUG
  # print(sorted(list(all_ngrams[1].keys())))
  # input()
  # print("in" in al)
  t1 = time.time()
  join_entities(sent_ent_list)
  relev_entities = {
                  "LOC": [],
                  "ORG": [],
                  "PER": [],
                  }

  custom_param["state"]["ngram"] = {x : [] for x in relev_entities.keys()}
  # get the vector for each entity
  for sent in sent_ent_list:
    # print(sent)
    # removing words not in vocab
    temp_list = []
    for i in range(len(sent)):
      flag = False
      if sent[i][1] in relev_entities.keys():
        flag = True
        temp_list.append(sent[i])
      elif (sent[i][0],) in all_ngrams[1].keys():
        temp_list.append(sent[i])
      # print(sent[i], flag)
    sent = temp_list
    # print(sent)
    for i, _ in enumerate(sent):
      if sent[i][1] in relev_entities.keys():
        # print(sent[i])
        # try with both relev and non-relev tag
        rel_phrase = get_ngram_phrase(sent, i, "REL")
        non_rel_phrase = get_ngram_phrase(sent, i, "NONREL")
        custom_param["state"]["ngram"][sent[i][1]].append((sent[i][0], (rel_phrase)))
        if stupid_backoff_score(rel_phrase) > stupid_backoff_score(non_rel_phrase):
            relev_entities[sent[i][1]].append(sent[i][0])

  # print(relev_entities)
  # print("Time taken: ", time.time()-t1)
  return relev_entities

def main():
  tester = Tester(custom_entity_detect_func, size=-1, stop=False,)
  tester.test()
  tester.score(True)

if __name__ == "__main__":
  main()