# Testing framework to check the efficiency of different
# methods to detect relevant entities in text
# Data set needs to be prepared and passed
import copy
import json
import os
import time

from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize

def_baseDir = "E:\College\IR\Entity"

def processSegment(segment, stop_words):
  tempSegment = word_tokenize(segment)
  # tempSegment = pattern.sub(" ", segment)
  # tempSegment = tempSegment.split()
  tempSegment = [word for word in tempSegment if not word in stop_words]

  return tempSegment

eval_dict = {
      "LOC" : [],
      "ORG" : [],
      "PER" : []
      }

eval_ = {
  "precision" : eval_dict,
  "recall"    : copy.deepcopy(eval_dict),
  "f_measure" : copy.deepcopy(eval_dict),
}

class Tester:
  def __init__(self, custom_entity_detect_func, baseDir=def_baseDir, size=-1, 
    stop=True, tagger="Stanford"):
    self.baseDir = baseDir
    self.test_sz = size
    self.stopFlag = stop
    self.tagger = tagger
    self.eval_ = eval_
    self.custom_entity_detect_func = custom_entity_detect_func

  def test(self):
    jsonDir = "tagged_dataset"
    jsonFiles = os.listdir(os.path.join(self.baseDir, jsonDir))
    test_ctr = 0

    for file in jsonFiles:
      t1 = time.time()
      if self.test_sz != -1 and test_ctr >= self.test_sz:
        break
      test_ctr += 1

      json_dict = json.load(open(os.path.join(self.baseDir, jsonDir, file)))
      content = json_dict["content"]

      sentence_list = sent_tokenize(content)
      # Removing noisy sentences
      temp_list = []
      for sent in sentence_list:
        if len(sent) > 2:
          temp_list.append(sent)
      sentence_list = temp_list

      # stop-words optional
      stop_words = set([])
      if self.stopFlag:
        stop_words = set(stopwords.words('english'))

      # tokenize and removve stop words
      sentence_tokens_list = [processSegment(sent,
        stop_words) for sent in sentence_list]

      if self.tagger == "Stanford":
        # stanford - ner tagger
        st_tagger = StanfordNERTagger(os.path.join(self.baseDir,
          'stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'),
                              os.path.join(self.baseDir,
                              'stanford-ner/stanford-ner.jar'))
      else:
        # spacy
        pass

      # each element is a list containing the tuples -
      # (word, entity_type, position in text) for each sentence
      sent_ent_list = []

      pos = 1
      sent_ent_list = st_tagger.tag_sents(sentence_tokens_list)
      for i, sent in enumerate(sent_ent_list):
        # add global position of each entity
        for j, elem in enumerate(sent):
          elem = (elem[0], elem[1], pos)
          pos += 1
          sent[j] = elem
        sent_ent_list[i] = sent

      # expected return type - dict containg the primary entities
      # of each type - LOC, ORG, PER with the these specific key names
      print("TIME BEFORE CUSTOM FUNC: %s" %(time.time() - t1))
      custom_relev_entities = self.custom_entity_detect_func(sent_ent_list,
                              sentence_list, content)

      t1 = time.time()
      self.evaluate(custom_relev_entities, json_dict)
      print("TIME TO EVALUATE: %s" %(time.time() - t1))
  # Measure the precision, recall and f1 for the given file
  def evaluate(self, custom_relev_entities, json_dict):
      # evaluate the custom function
      json_format = {
            "LOC"   : "Event",
            "ORG"   : "Accused",
            "PER"   : "Accused",
      }

      for ent_type in json_format.keys():
        relev_ent = []
        for ent in json_dict[ent_type]:
          if ent[2] == json_format[ent_type]:
            # convert to lower
            relev_ent.append(ent[0].lower())

        relev_ent = set(relev_ent)
        # print (relev_ent)
        temp_set = set(custom_relev_entities[ent_type])
        common = len(relev_ent.intersection(temp_set))
        # CHECK IF CORRECT
        if len(temp_set) > 0:
          precision = common/len(temp_set)
        else:
          precision = 1
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
  def score(self):
    for ent_type in eval_dict.keys():
      print("Entity Type: --------------------", ent_type, "--------------------\n")
      for measure in eval_.keys():
        print("Average %s: %s" %(measure, 
          sum(self.eval_[measure][ent_type])/len(self.eval_[measure][ent_type]) 
          ))
      print("\n")
