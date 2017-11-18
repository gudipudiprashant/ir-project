# Custom detect function based on frequency
import time

from collections import Counter
from Entity_test import Tester, get_all_entities

# computes the frequency of each entity
def compute_freq(sent_ent_list, coref_chain_list=None):
  relev_entitites = get_all_entities(sent_ent_list)
  # count the number of times entity occurs using Counter
  for typ in relev_entitites:
    relev_entitites[typ] = Counter(relev_entitites[typ])
  # use coref count of the words
  if coref_chain_list is not None:
    for typ in relev_entitites.keys():
      for ent in relev_entitites[typ].keys():
        count = 0
        for chain in coref_chain_list:
          dup_ct = 0
          for ent_in_chain in chain:
            if ent == ent_in_chain:
              dup_ct += 1
              # print(ent, chain)
          if dup_ct != 0:
            count += len(chain) - dup_ct
        relev_entitites[typ][ent] += count

  return relev_entitites

def custom_entity_detect_func(sent_ent_list, sentence_list, content,
  custom_param):
  # t1 = time.time()
  threshold = custom_param.get("threshold", 2)
  coref_chain_list = custom_param.get("coref")

  relev_entitites = compute_freq(sent_ent_list, coref_chain_list)
  # threshold the relevant entities:
  # Entities occuring more than half the max is valid
  for typ in relev_entitites.keys():
    relev = []
    if len(relev_entitites[typ].keys()) == 0:
      relev_entitites[typ] = relev
      continue
    max_val = max(relev_entitites[typ].values())
    for ent in relev_entitites[typ].keys():
      if relev_entitites[typ][ent] > max_val/threshold:
        relev.append(ent)
    relev_entitites[typ] = relev
  
  # print("Time taken: %s" %(time.time() - t1))
  return relev_entitites


def main():
  tester = Tester(custom_entity_detect_func, size=-1, stop=False,)
  tester.test()
  tester.score(True)

if __name__ == "__main__":
  main()


