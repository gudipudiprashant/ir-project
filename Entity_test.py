# Testing framework to check the efficiency of different
# methods to detect relevant entities in text
# Data set needs to be prepared and passed
import copy
import json
import os
import random
import re
import time

import config
import java_handler
import json_parse


from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
# from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize

def_baseDir = "E:\College\IR\Entity"
if hasattr(config,"base_dir"):
  def_baseDir = config.base_dir

lemmatizer = WordNetLemmatizer()

eval_dict = {
      "LOC" : [],
      "ORG" : [],
      "PER" : []
      }
relev_category_map = {"ORGANIZATION":"ORG", "LOCATION":"LOC", "PERSON":"PER"}


# joins parts of the same entity
def join_entities(sent_ent_list, extra = False):
  for i, sent in enumerate(sent_ent_list):
    temp_list = []
    j = 0
    while (j < len(sent)):
      joined_ent , ent_typ, ent_pos = sent[j]
      # join parts of the same entity
      while (j+1 < len(sent) and sent[j+1][1] != "O"
        and sent[j+1][1] == ent_typ):
        joined_ent += " " + sent[j+1][0]
        j += 1
      joined_ent = transform(joined_ent)
      j += 1
      # add entity and it's type
      if ent_typ == "O":
        joined_ent = lemmatizer.lemmatize(joined_ent)
        joined_ent = lemmatizer.lemmatize(joined_ent, pos="v")
      if ent_typ in relev_category_map:
        ent_typ = relev_category_map[ent_typ]
      if not extra:
        temp_list.append((joined_ent, ent_typ))
      else:
        temp_list.append((joined_ent, ent_typ, ent_pos))
    sent_ent_list[i] = temp_list
  # print(sent_ent_list)

def transform(word):
  word = word.lower()
  word = re.sub("[^\w_\s]+", "",word)
  return word

# returns all the entities in the given list in lower-case.
# if extra is set - returns 3 tuple - entity, sentence_number, position
def get_all_entities(sent_ent_list, extra=False):
  ner_entities =  {
                    "LOC" : [],
                    "ORG" : [],
                    "PER" : [],
                  }
  mapper = {
    "LOCATION": "LOC", "ORGANIZATION": "ORG", "PERSON": "PER",
    "NORP": "ORG", "FACILITY":  "ORG", "ORG": "ORG", "GPE": "LOC",
    "LOC": "LOC", "PER": "PER"
  }
  # join the entities and put them in the corresponding class
  ctr = 0
  for sent_num, sent in enumerate(sent_ent_list):
    i = 0
    # print(sent)
    while i < len(sent):
      joined_ent = sent[i][0]
      typ = sent[i][1]
      if typ != "O":
        while i+1 < len(sent) and sent[i+1][1] == typ:
          joined_ent += " " + sent[i+1][0]
          i += 1
          ctr += 1
      joined_ent = transform(joined_ent)
      if typ in mapper.keys(): 
        # print(joined_ent)
        if extra:
          # appends(entity, sentence number, position in doc)
          ner_entities[mapper[typ]].append((joined_ent.lower(), sent_num, ctr))
        else:  
          ner_entities[mapper[typ]].append(joined_ent.lower())
      i += 1
      ctr += 1

  return ner_entities

def processSegment(segment, stop_words):
  tempSegment = word_tokenize(segment)
  # tempSegment = pattern.sub(" ", segment)
  # tempSegment = tempSegment.split()
  tempSegment = [word for word in tempSegment if not word in stop_words]
  return tempSegment

def add_position_ent_list(sent_ent_list):
  pos = 1
  for i, sent in enumerate(sent_ent_list):
    # add global position of each entity
    for j, elem in enumerate(sent):
      elem = (elem[0], elem[1], pos)
      pos += 1
      sent[j] = elem
    sent_ent_list[i] = sent
  return sent_ent_list

def get_clean_sentences(sentence_list, sent_ent_list,debug=False):
  # sentence_list = sent_tokenize(content)
  # Removing noisy sentences
  temp_list = []
  temp_ent_list = []
  for ii, sent in enumerate(sentence_list):
    # print("In get clean: ", sent)
    word_ct = 0
    for word in sent:
      if word not in config.stop_words:
        word_ct += 1
    if word_ct > 3:
      trip_dot_pos = []
      for i, elem in enumerate(sent):
        if elem in [". . .", ":", ". .", ]:
          trip_dot_pos.append(i)
      start = 0
      for pos in trip_dot_pos:
        if debug:
          print(sent, pos, sent[start: pos])
        temp_list.append(sent[start : pos] + ["."])
        temp_ent_list.append(sent_ent_list[ii][start : pos] + [(".", "O", -1)])
        start = pos+1
      temp_list.append(sent[start : -1] + ["."])
      temp_ent_list.append(sent_ent_list[ii][start : -1] + [(".", "O", -1)])
      # print(temp_list)  
  return temp_list, temp_ent_list

# Returns the relevant entities in json_dict in lower case
def get_relev_entities(json_dict):
  json_format = {
      "LOC"   : ["Event", "Assoc_Event", "Source", "Victim"],
      "ORG"   : ["Accused", "Assoc_Accused", "Victim"],
      "PER"   : ["Accused", "Assoc_Accused", "Victim"],
    }
  relev_ent_dict = {ent_type: set([]) for ent_type in json_format.keys()}

  for ent_type in relev_ent_dict.keys():
    relev_ent = []
    for ent in json_dict[ent_type]:
      if ent[2] in json_format[ent_type]:
        # convert to lower
        relev_ent.append(transform(ent[0]))
    relev_ent_dict[ent_type] = set(relev_ent)
  return relev_ent_dict  


# returns json_dict_list
def run_ner_coref(jsonDir, jsonFiles):
  # list of 2 tuples - (json file name, json_dict)
  json_dict_list, done_json_list = [], []
  # ner and coref is not rerun on alraedy present files
  if not os.path.exists("out/"):
    os.makedirs("out/")
  already_present = os.listdir("out/")

  ctr = 0
  for file in jsonFiles:
    ctr += 1
    json_dict = json.load(open(os.path.join(jsonDir, file)))
    # Don't append it if it is already present in folder - out
    if file+".json" in already_present:
      done_json_list.append((file, json_dict))
    else:
      json_dict_list.append((file, json_dict))
  # run core-nlp java file
  t1 = time.time()
  if len(json_dict_list) != 0:
    json_parse.dump_json(json_dict_list)
  print("Time taken by java file to tag and coref: ", time.time() - t1)

  json_dict_list += done_json_list
  return json_dict_list

# Class for the testing framework
class Tester:
  def __init__(self, custom_entity_detect_func, baseDir=def_baseDir, size=-1, 
    stop=True, tagger="Stanford", eval_NER=True, custom_param={}):
    self.baseDir = baseDir
    self.test_sz = size
    self.stopFlag = stop
    self.tagger = tagger
    self.eval_ = {
                    "precision" : copy.deepcopy(eval_dict),
                    "recall"    : copy.deepcopy(eval_dict),
                    "f_measure" : copy.deepcopy(eval_dict),
                    "accuracy"  : copy.deepcopy(eval_dict),
                  }
    self.custom_entity_detect_func = custom_entity_detect_func
    # Evaluates only the Entities returned by NER as ground truth
    self.eval_NER = eval_NER
    self.custom_param = custom_param

  def test(self):
    jsonDir = config.test_dataset_folder
    # debug
    # jsonFiles = os.listdir(os.path.join(self.baseDir, jsonDir))[17:18]

    jsonFiles = os.listdir(os.path.join(self.baseDir, jsonDir))[:self.test_sz]
    shuf = False
    if hasattr(config,"shuffle"):
      shuf = config.shuffle

    if shuf:
      random.shuffle(jsonFiles)
    # jsonFiles = jsonFiles[0:self.test_sz]
    # jsonFiles = jsonFiles[600:]

    if self.tagger == "Stanford":
      jsonDir = os.path.join(self.baseDir, jsonDir)
      json_dict_list = run_ner_coref(jsonDir, jsonFiles)

      t1 = time.time()
      ctr = 0
      for file, json_dict in json_dict_list:
        self.custom_param["filename"] = file
        self.custom_param["state"] = {}
        ctr += 1
        # print(ctr)
        sentence_list_old, sent_ent_list, coref_chain_list = \
          java_handler.get_sent_token_coref(os.path.join("out/", file+".json"))

        sentence_list, sent_ent_list = get_clean_sentences(sentence_list_old,
                    sent_ent_list)
        try:
          self.custom_param["title"] = json_dict.get("title", sentence_list[0])
        except Exception as e:
          # get_clean_sentences(sentence_list_old, sent_ent_list, True)
          pass
        self.custom_param["coref"] = coref_chain_list      
        # call the entity detect function
        custom_relev_entities = self.custom_entity_detect_func(sent_ent_list,
                                sentence_list, json_dict["content"], 
                                self.custom_param)
          
        self.evaluate(custom_relev_entities, json_dict, sent_ent_list)
        
      print("TIME TO EVALUATE: %s" %(time.time() - t1))  


    if self.tagger == "spacy":
      import spacy
      # nlp = spacy.load('en')
      # t_1 = time.time()
      # nlp = spacy.load("en_core_web_lg")
      # print("TO LOAD SPACY:")
      # print(time.time() - t_1)

      nlp = self.custom_param["nlp_spacy"]

      for file in jsonFiles:
        if self.test_sz != -1 and test_ctr >= self.test_sz:
          break
        test_ctr += 1

        json_dict = json.load(open(os.path.join(self.baseDir, jsonDir, file)))
        content = json_dict["content"]

        #insert title to custom_param
        if json_dict.get("title") is not None:
          self.custom_param["title"] = json_dict["title"]
        else:
          print("TITLE DOES NOT EXIST!!!!")
          input()

        sentence_list = get_clean_sentences(content)
        # each element is a list containing the tuples -
        # (word, entity_type, position in text) for each sentence
        sent_ent_list = []

        pos = 1
        for i in range(len(sentence_list)):
          sentence_list[i] = nlp(sentence_list[i])
          temp_list = []
          for word in sentence_list[i]:
            temp_list.append((word.text, word.ent_type_, pos))
            pos += 1
          sent_ent_list.append(temp_list)
        # print("TIME BEFORE CUSTOM FUNC: %s" %(time.time() - t1))
        custom_relev_entities = self.custom_entity_detect_func(sent_ent_list,
                                sentence_list, content, self.custom_param)
        # t1 = time.time()
        self.evaluate(custom_relev_entities, json_dict, sent_ent_list)
        # print("TIME TO EVALUATE: %s" %(time.time() - t1))

  # Measure the precision, recall and f1 for the given file
  def evaluate(self, custom_relev_entities, json_dict, sent_ent_list):
    # Format of relevant entities as marked in the tagged json files
      # if self.eval_NER:
      ner_entities = get_all_entities(sent_ent_list)
      # print(ner_entities)
      relev_ent_dict = get_relev_entities(json_dict)
      # print(relev_ent_dict)
      # print(relev_ent_dict)
      for ent_type in relev_ent_dict.keys():
        relev_ent = relev_ent_dict[ent_type]
        # Evaluates the custom function on the restricted set
        # of entities - the ground truth/tagged relevant entities
        # intersection with the NER entities to better understand
        # the shortcomings of the custom function
        ner_entities[ent_type] = set(ner_entities[ent_type])
        if self.eval_NER:
          # print("yeahs")
          # input()
          relev_ent = relev_ent.intersection(ner_entities[ent_type])

        non_relev_ent = ner_entities[ent_type] - relev_ent

        custom_rel = set([ent.lower() for ent in custom_relev_entities[ent_type]])
        tp = len(relev_ent.intersection(custom_rel))
        custom_non_relev = ner_entities[ent_type] - custom_rel
        tn = len(non_relev_ent.intersection(custom_non_relev))

        # Accuracy = (tp+tn)/(tp+tn+fp+fn)
        accuracy = 1
        if len(ner_entities[ent_type]) != 0:
          accuracy = (tp+tn)/len(ner_entities[ent_type])
        # print (ent_type, relev_ent, custom_rel)
        # CHECK IF PRECISION hsould be 1 or 0 in the edge case
        if len(custom_rel) > 0:
          precision = tp/len(custom_rel)
        else:
          precision = 1

        # ### DEBUGGER ####
        # if precision <= 0.5:
        #   print(self.custom_param["filename"])
        #   print("Entity Type: ", ent_type)
        #   print("-----------------------")
        #   print("System returned:",custom_rel ,"\n", 
        #     self.custom_param["state"]["ngram"])
        #   print("---------------------------------------------")
        #   print("Ground Truth:", relev_ent)
        #   input()

        if len(relev_ent) > 0:
          recall = tp/len(relev_ent)
        else:
          recall = 1

        self.eval_["accuracy"][ent_type].append(accuracy)
        self.eval_["precision"][ent_type].append(precision)
        self.eval_["recall"][ent_type].append(recall)
        divisor = precision + recall
        if divisor == 0:
          divisor = 1
        self.eval_["f_measure"][ent_type].append(
          2*precision*recall/divisor)

  # Measures the average precision, recall and f1 measure of the custom entity
  # detect function for the given data set
  def score(self, print_flag=False):
    for ent_type in eval_dict.keys():
      if print_flag:
        print("Entity Type: --------------------", ent_type, "--------------------\n")
      # Calculate the average of the performance metrics
      for measure in self.eval_.keys():
        self.eval_[measure][ent_type] = (sum(self.eval_[measure][ent_type])/
          len(self.eval_[measure][ent_type]))

        if print_flag:
          print("Average %s: %s" %(measure, self.eval_[measure][ent_type]))
      if print_flag:
        print("\n")

    return self.eval_
