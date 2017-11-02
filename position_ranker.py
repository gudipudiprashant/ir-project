# Custom detect function based on frequency
import time
from Entity_test import Tester

def custom_entity_detect_func(sent_ent_list, sentence_list, content, custom_param):
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

  # Initial implementation is to use a parameter for the number of sentences as threshold.

  ent_set = set()
  sent_counter = 0

  new_entity_count_list = []
  sentence_threshold = custom_param.get("threshold",3)

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
    if(sent_counter >= sentence_threshold):
      break
    # print(count_new_entities)
    # print(new_entity_list)


  for sent_new_entity_list in new_entity_count_list:
    for ent_tuple in sent_new_entity_list:
      typ = ent_tuple[1]
      ent = ent_tuple[0]

      relev_entitites[mapper[typ]].append(ent.lower())

  return relev_entitites


def main():
  tester = Tester(custom_pos_func, size=10, stop=False)
  tester.test()
  tester.score()

if __name__ == "__main__":
  main()


