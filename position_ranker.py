# Custom detect function based on frequency
import time
from Entity_test import Tester

def custom_freq_func(sent_ent_list, sentence_list, content):
  t1 = time.time()
  relev_entitites = {
                    "LOC": {},
                    "ORG": {},
                    "PER": {},
                    }
  mapper = {"LOCATION": "LOC", "ORGANIZATION": "ORG", "PERSON": "PER"}
  # print(sent_ent_list)
  for sent in sent_ent_list:
    i = 0
    while i < len(sent):
      joined_ent = sent[i][0]
      typ = sent[i][1]
      if typ != "O":
        while i+1 < len(sent) and sent[i+1][1] == typ:
          joined_ent += " " + sent[i+1][0]
          i += 1
      if typ in mapper.keys(): 
        if joined_ent.lower() in relev_entitites[mapper[typ]]:
          relev_entitites[mapper[typ]][joined_ent.lower()] += 1
        else:
          relev_entitites[mapper[typ]][joined_ent.lower()] = 1
      i += 1

  # print(relev_entitites, sent_ent_list)

  # Entities occuring more than half the max is valid
  for typ in relev_entitites.keys():
    relev = []
    if len(relev_entitites[typ].keys()) == 0:
      relev_entitites[typ] = relev
      continue
    max_val = max(relev_entitites[typ].values())
    for ent in relev_entitites[typ].keys():
      if relev_entitites[typ][ent] > max_val/2:
        relev.append(ent)
    relev_entitites[typ] = relev
  # print(relev_entitites)
  print("Time taken: %s" %(time.time() - t1))
  return relev_entitites


def main():
  tester = Tester(custom_freq_func, size=10, stop=False)
  tester.test()
  tester.score()

if __name__ == "__main__":
  main()


