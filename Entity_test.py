# Testing framework to check the efficiency of different
# methods to detect relevant entities in text
# Data set needs to be prepared and passed
import copy
import json
import os
import time

import config

from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize

def_baseDir = "E:\College\IR\Entity"
if hasattr(config,"base_dir"):
  def_baseDir = config.base_dir


eval_dict = {
      "LOC" : [],
      "ORG" : [],
      "PER" : []
      }


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
    "LOC": "LOC"
  }
  # join the entities and put them in the corresponding class
  ctr = 0
  for sent_num, sent in enumerate(sent_ent_list):
    i = 0
    while i < len(sent):
      joined_ent = sent[i][0]
      typ = sent[i][1]
      if typ != "O":
        while i+1 < len(sent) and sent[i+1][1] == typ:
          joined_ent += " " + sent[i+1][0]
          i += 1
          ctr += 1
      if typ in mapper.keys(): 
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

def get_clean_sentences(content):
  sentence_list = sent_tokenize(content)
  # Removing noisy sentences
  temp_list = []
  for sent in sentence_list:
    if len(sent) > 2:
      temp_list.append(sent)
  return temp_list

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
        relev_ent.append(ent[0].lower())
    relev_ent_dict[ent_type] = set(relev_ent)
  return relev_ent_dict  

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
                  }
    self.custom_entity_detect_func = custom_entity_detect_func
    # Evaluates only the Entities returned by NER as ground truth
    self.eval_NER = eval_NER
    self.custom_param = custom_param

  def test(self):
    jsonDir = config.test_dataset_folder
    jsonFiles = os.listdir(os.path.join(self.baseDir, jsonDir))

    # stop-words optional
    stop_words = set([])
    if self.stopFlag:
      stop_words = set(stopwords.words('english'))

    test_ctr = 0
    
    t1 = time.time()

    if self.tagger == "Stanford":
      # stanford - ner tagger
      st_tagger = StanfordNERTagger(os.path.join(self.baseDir,
        'stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'),
                            os.path.join(self.baseDir,
                            'stanford-ner/stanford-ner.jar'))
      # work on batch_sz files each time
      # can make this a custom parameter
      batch_sz = self.custom_param.get("Batch_size", 250)
      break_flag = False
      for ii in range(0, len(jsonFiles), batch_sz):
        json_dict_list = []
        all_sentences_list = []
        all_sent_tokens_list = []
        
        for test_ctr in range(ii, ii + batch_sz):
          # t1 = time.time()
          if self.test_sz != -1 and test_ctr >= self.test_sz:
            break_flag = True
            break
          # Load the json tagged dataset
          
          if test_ctr >= len(jsonFiles):
            break  
          file = jsonFiles[test_ctr]
          # print()
          # print("FILENAME:")
          # print(file)
          # print()
          json_dict = json.load(open(os.path.join(self.baseDir, jsonDir, file)))
          # get the content
          content = json_dict["content"]
          json_dict_list.append(json_dict)
          # get individual sentences
          sentence_list = get_clean_sentences(content)
          all_sentences_list.append(sentence_list)
          # break down sentences to tokens for the Stanford NER tagger
          all_sent_tokens_list += [processSegment(sent,
                      stop_words) for sent in sentence_list]

        all_sent_ent_list = st_tagger.tag_sents(all_sent_tokens_list)
        # print(all_sent_ent_list)
        file_start = 0
        t1 = time.time()
        for i, sentence_list in enumerate(all_sentences_list):
          # Retrieve each file's sentence_entity_list :
          # each element is a list containing the tuples -
          # (word, entity_type, position in text) for each sentence
          sent_ent_list = all_sent_ent_list[file_start : file_start+len(sentence_list)]
          file_start += len(sentence_list)
          sent_ent_list = add_position_ent_list(sent_ent_list)
          # print("TIME BEFORE CUSTOM FUNC: %s" %(time.time() - t1))

          #insert title to custom_param
          if json_dict_list[i].get("title") is not None:
            self.custom_param["title"] = json_dict_list[i]["title"]
          else:
            continue
          
          custom_relev_entities = self.custom_entity_detect_func(sent_ent_list,
                                  sentence_list, json_dict_list[i]["content"], 
                                  self.custom_param)
          
          self.evaluate(custom_relev_entities, json_dict_list[i], sent_ent_list)
        
        print("TIME TO EVALUATE: %s" %(time.time() - t1))  
        if break_flag:
          break


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
      if self.eval_NER:
        ner_entities = get_all_entities(sent_ent_list)
      
      relev_ent_dict = get_relev_entities(json_dict)
      # print(relev_ent_dict)
      for ent_type in relev_ent_dict.keys():
        relev_ent = relev_ent_dict[ent_type]
        # Evaluates the custom function on the restricted set
        # of entities - the ground truth/tagged relevant entities
        # intersection with the NER entities to better understand
        # the shortcomings of the custom function
        if self.eval_NER:
          # print("yeahs")
          # input()
          relev_ent = relev_ent.intersection(ner_entities[ent_type])

        temp_set = set([ent.lower() for ent in custom_relev_entities[ent_type]])
        common = len(relev_ent.intersection(temp_set))
        # print (ent_type, relev_ent, temp_set)
        # CHECK IF PRECISION hsould be 1 or 0 in the edge case
        if len(temp_set) > 0:
          precision = common/len(temp_set)
        else:
          precision = 1

        # if precision <= 0.5:
        #   # print(json_dict["content"])
        #   print("Entity Type: ", ent_type)
        #   print("-----------------------")
        #   print("System returned:", temp_set)
        #   print("---------------------------------------------")
        #   print("Ground Truth:", relev_ent)
        #   # input()

        if len(relev_ent) > 0:
          recall = common/len(relev_ent)
        else:
          recall = 1

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
