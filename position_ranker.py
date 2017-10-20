# Custom detect function based on frequency
import time
from Entity_test import Tester

def custom_freq_func(sent_ent_list, sentence_list, content, custom_param):
  t1 = time.time()
  relev_entitites = {
                    "LOC": [],
                    "ORG": [],
                    "PER": [],
                    }
  mapper = {"LOCATION": "LOC", "ORGANIZATION": "ORG", "PERSON": "PER"}

  # print(sent_ent_list)


  # Assumption is that the relevant entities will only be found at the top of
  # the article, and the number of new relevant entities decreases as the article
  # goes on. 

  # So the method is to find the number of new entities per sentence. We assume that
  # the number of entities will drop down smoothly (like an exponential curve for now).
  # So using this assumption, having a threshold of 1/e of the top sentence is chosen.

  ent_set = set()
  sent_counter = 0

  new_entity_count_list = []
  # for sent_list in sent_ent_list:
  #   count_new_entities = 0
  #   new_entity_list = []
  #   for ent_tuple in sent_list:
  #     if ent_tuple[1] in mapper.keys() and ent_tuple[0] not in ent_set:
  #       # print(ent_tuple)
  #       ent_set.add(ent_tuple[0])
  #       new_entity_list.append(ent_tuple)
  #       count_new_entities += 1

  #   new_entity_count_list.append(new_entity_list)

  #   # print(sentence_list[sent_counter])
  #   sent_counter += 1
  #   print(count_new_entities)






  # print(sent_ent_list)
  for sent in sent_ent_list:
    i = 0
    count_new_entities = 0
    new_entity_list = []
    while i < len(sent):
      joined_ent = sent[i][0]
      typ = sent[i][1]
      if typ != "O":
        while i+1 < len(sent) and sent[i+1][1] == typ:
          joined_ent += " " + sent[i+1][0]
          i += 1
      if typ in mapper.keys() and joined_ent not in ent_set: 
        ent_set.add(joined_ent)
        new_entity_list.append((joined_ent, typ))
        count_new_entities += 1
      i += 1

    new_entity_count_list.append(new_entity_list)

    # print(sentence_list[sent_counter])
    sent_counter += 1
    print(count_new_entities)
    print(new_entity_list)


  for sent_new_entity_list in new_entity_count_list:
    for ent_tuple in sent_new_entity_list:
      typ = ent_tuple[1]
      ent = ent_tuple[0]

      relev_entitites[mapper[typ]].append(ent.lower())

  # # print(relev_entitites, sent_ent_list)

  # # Entities occuring more than half the max is valid
  # for typ in relev_entitites.keys():
  #   relev = []
  #   if len(relev_entitites[typ].keys()) == 0:
  #     relev_entitites[typ] = relev
  #     continue
  #   max_val = max(relev_entitites[typ].values())
  #   for ent in relev_entitites[typ].keys():
  #     if relev_entitites[typ][ent] > max_val/2:
  #       relev.append(ent)
  #   relev_entitites[typ] = relev
  # # print(relev_entitites)
  # print("Time taken: %s" %(time.time() - t1))
  return relev_entitites


def main():
  tester = Tester(custom_freq_func, size=10, stop=False)
  tester.test()
  tester.score()

if __name__ == "__main__":
  main()


