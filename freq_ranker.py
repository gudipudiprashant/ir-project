# Custom detect function based on frequency
import time

from collections import Counter
from Entity_test import Tester, get_all_entities

def custom_entity_detect_func(sent_ent_list, sentence_list, content,
  custom_param):
  # t1 = time.time()
  relev_entitites = get_all_entities(sent_ent_list)

  threshold = custom_param.get("threshold", 2)
  for typ in relev_entitites:
    relev_entitites[typ] = Counter(relev_entitites[typ])

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
  tester = Tester(custom_entity_detect_func, size=10, stop=False,)
  tester.test()
  tester.score(True)

if __name__ == "__main__":
  main()


