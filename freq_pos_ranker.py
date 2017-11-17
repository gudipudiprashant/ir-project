# Custom detect function based on the formula from Online Event Detection Paper
import math
import time

from Entity_test import Tester

def custom_entity_detect_func(sent_ent_list, sentence_list, content,
  custom_param):
  # t1 = time.time()
  relev_entities = {
                    "LOC": {"$N" : 0},
                    "ORG": {"$N" : 0},
                    "PER": {"$N" : 0},
                    }
  mapper = {"LOCATION": "LOC", "ORGANIZATION": "ORG", "PERSON": "PER"}
  threshold = custom_param.get("threshold", 2)
  # print(sent_ent_list)
  for sent in sent_ent_list:
    i = 0
    while i < len(sent):
      joined_ent = sent[i][0]
      typ = sent[i][1]
      pos = sent[i][2]
      if typ != "O":
        while i+1 < len(sent) and sent[i+1][1] == typ:
          joined_ent += " " + sent[i+1][0]
          i += 1
      if typ in mapper.keys():
        relev_entities[mapper[typ]]["$N"] += 1
        if joined_ent.lower() in relev_entities[mapper[typ]]:
          relev_entities[mapper[typ]][joined_ent.lower()][0] += 1
        else:
          relev_entities[mapper[typ]][joined_ent.lower()] = [1, relev_entities[mapper[typ]]["$N"]]
      i += 1

  # SCORE THE ENTITIES
  for typ in relev_entities.keys():
    N = relev_entities[typ]["$N"]
    for ent in relev_entities[typ].keys():
      if ent != "$N":
        relev_entities[typ][ent] = ((1 + relev_entities[typ][ent][0]/N) *
          (1+ N - relev_entities[typ][ent][1]) / (N*(N+1)/2))
    del(relev_entities[typ]["$N"])  

  # CUT_OFF FUNCTION
  # Entities occuring more than half the max is valid
  for typ in relev_entities.keys():
    relev = []
    if len(relev_entities[typ].keys()) == 0:
      relev_entities[typ] = relev
      continue
    max_val = max(relev_entities[typ].values())
    for ent in relev_entities[typ].keys():
      if relev_entities[typ][ent] > max_val/threshold:
        relev.append(ent)
    relev_entities[typ] = relev
  # print("Time taken: %s" %(time.time() - t1))

  return relev_entities


def main():
  t1 = time.time()
  tester = Tester(custom_entity_detect_func, size=-1, stop=False)
  tester.test()
  print (tester.score())
  print("TIme taken: ", time.time()-t1)

if __name__ == "__main__":
  main()


