import numpy as np
import os
import config
import java_handler

from Entity_test import Tester, join_entities
from gen_ent_vectors import *
from pe_neural_net import PrimaryEntityNeuralNet
from freq_ranker import compute_freq

def pad(vec_list, left):
  pad_num = max(0, radius - len(vec_list))
  padder = [np.zeros(config.word2vec_dim) for i in range(pad_num)]
  return (padder + vec_list) if left else (vec_list + padder)

def generate_neural_net(nn_json, nn_weights):
  baseDir = config.base_dir
  # json_dir = config.train_dataset_folder
  json_dir = config.train_dataset_folder
  json_dir = os.path.join(baseDir, json_dir)
  jsonFiles = os.listdir(json_dir)
  json_dict_list = run_ner_coref(json_dir, jsonFiles)
  print("Starting training of neural net...")
  t1 = time.time()
  neural_net = PrimaryEntityNeuralNet()
  neural_net.compile()
  ctr = 0
  for file, json_dict in json_dict_list:
    ctr += 1
    sentence_list_old, sent_ent_list, coref_chain_list = \
      java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))
    doc_len = sum([len(sent) for sent in sent_ent_list])
    freq_dict = compute_freq(sent_ent_list)
    sentence_list, sent_ent_list = get_clean_sentences(sentence_list_old,
                sent_ent_list)
    # joins parts of the same entity
    join_entities(sent_ent_list, extra = True)
    # get relev and non relev entity vectors from each file
    relev_entities = get_relev_entities(json_dict)
    all_relev = set()
    for ent_typ in relev_entities:
      all_relev.update(relev_entities[ent_typ])

    # get the vector for each entity
    for sent in sent_ent_list:
      for i, elem in enumerate(sent):
        word, catg, pos = elem
        if catg in relev_category_map.values():
          v_b, v_f = get_entity_vector(sent, i, True)
          relev = True if (word in all_relev) else False
          freq = freq_dict[catg][word] if (word in freq_dict[catg]) else 0
          n_pos = pos/doc_len
          neural_net.add_training_data(catg, pad(v_b[0], left = True), pad(v_f[0], left = False),
             freq, n_pos, relev)
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
  freq_dict = compute_freq(sent_ent_list)
  doc_len = sum([len(sent) for sent in sent_ent_list])
  join_entities(sent_ent_list, extra = True)
  relev_entities = {
                  "LOC": [],
                  "ORG": [],
                  "PER": [],
                  }
  # get the vector for each entity
  for sent in sent_ent_list:
    for i, _ in enumerate(sent):
      word, catg, pos = sent[i]
      if catg in relev_entities.keys():
        ent_vec_back, ent_vec_forw = get_entity_vector(sent, i, True)
        freq = freq_dict[catg][word] if (word in freq_dict[catg]) else 0
        n_pos = pos/doc_len
        if neural_net.predict(catg, pad(ent_vec_back[0], left = True),
            pad(ent_vec_forw[0], left = False), freq, n_pos) == True:  
          relev_entities[catg].append(word)

  # print(time.time()-t1)
  return relev_entities

def main():
  tester = Tester(custom_entity_detect_func, size=-1, stop=False,)
  tester.test()
  tester.score(True)

if __name__ == "__main__":
  main()
