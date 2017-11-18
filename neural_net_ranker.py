import numpy as np
import os
import config
import java_handler

from Entity_test import Tester, join_entities
from gen_ent_vectors import *
from pe_neural_net import PrimaryEntityNeuralNet
from freq_ranker import compute_freq

def generate_neural_net(nn_json, nn_weights):
  baseDir = config.base_dir
  # json_dir = config.train_dataset_folder
  json_dir = config.train_dataset_folder
  json_dir = os.path.join(baseDir, json_dir)
  jsonFiles = os.listdir(json_dir)
  json_dict_list = run_ner_coref(json_dir, jsonFiles)

  nets = {"LOC" : None, "PER" : None, "ORG" : None}

  print("Starting training of neural net...")
  t1 = time.time()
  neural_net = PrimaryEntityNeuralNet()
  neural_net.compile()
  ctr = 0
  for file, json_dict in json_dict_list:
    ctr += 1
    sentence_list_old, sent_ent_list, coref_chain_list = \
      java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))

    freq_dict = compute_freq(sent_ent_list)
    sentence_list, sent_ent_list = get_clean_sentences(sentence_list_old,
                sent_ent_list)
    # joins parts of the same entity
    join_entities(sent_ent_list)
    # get relev and non relev entity vectors from each file
    relev_entities = get_relev_entities(json_dict)
    all_relev = set()
    for ent_typ in relev_entities:
      all_relev.update(relev_entities[ent_typ])

    # get the vector for each entity
    for sent in sent_ent_list:
      for i, elem in enumerate(sent):
        word, catg = sent[i][0], sent[i][1]
        if catg in relev_category_map.values():
          v_b, v_f = get_entity_vector(sent, i, True)
          relev = True if (word in all_relev) else False
          freq = freq_dict[catg][word] if (word in freq_dict[catg]) else 0
          neural_net.add_training_data(catg, v_b[1], v_f[1], freq, relev)
  # Train the network
  neural_net.train_network()
  # store the generated vector
  print("Saving NN model to file.")
  neural_net.save_to_file(nn_json, nn_weights)
  print("Time taken for whole process: ", time.time() - t1)
  return neural_net


def load_neural_net():
  if not os.path.exists(config.nn_json + ".LOC") \
      or (not os.path.exists(config.nn_weights + ".LOC")):
    print("Not present, building a new neural net")
    neural_net = generate_neural_net(config.nn_json, config.nn_weights)
  else:
    neural_net = PrimaryEntityNeuralNet()
    neural_net.load_from_file(config.nn_json, config.nn_weights)
    neural_net.compile()
    print("Loaded model from disk.")
     
  return neural_net

neural_net = load_neural_net()

def custom_entity_detect_func(sent_ent_list, sentence_list, content,
    custom_param):
  # t1 = time.time()
  join_entities(sent_ent_list)
  relev_entities = {
                  "LOC": [],
                  "ORG": [],
                  "PER": [],
                  }
  # get the vector for each entity
  for sent in sent_ent_list:
    # print(sent)
    for i, _ in enumerate(sent):
      if sent[i][1] in relev_entities.keys():
        # print(sent[i])
        ent_vec_back, ent_vec_forw = get_entity_vector(sent, i, True)
        if neural_net.predict(sent[i][1], ent_vec_back[1],
            ent_vec_forw[1], 1) == True:  
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
