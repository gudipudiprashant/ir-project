# Testing framework to check the efficiency of different
# methods to detect relevant entities in text
# Data set needs to be prepared and passed
import copy
import json
import spacy
import os
import time

from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize

def_baseDir = "E:\College\IR\Entity"

eval_dict = {
      "LOC" : [],
      "ORG" : [],
      "PER" : []
      }


# returns all the entities in the given list in lower-case.
def get_all_entities(sent_ent_list):
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
        ner_entities[mapper[typ]].append(joined_ent.lower())
      i += 1

  return ner_entities

def processSegment(segment, stop_words):
  tempSegment = word_tokenize(segment)
  # tempSegment = pattern.sub(" ", segment)
  # tempSegment = tempSegment.split()
  tempSegment = [word for word in tempSegment if not word in stop_words]

  return tempSegment


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
    jsonDir = "tagged_dataset"
    jsonFiles = os.listdir(os.path.join(self.baseDir, jsonDir))
    test_ctr = 0
    if self.tagger == "spacy":
      nlp = spacy.load('en')

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

      # each element is a list containing the tuples -
      # (word, entity_type, position in text) for each sentence
      sent_ent_list = []

      if self.tagger == "Stanford":
        # tokenize and removve stop words
        sentence_tokens_list = [processSegment(sent,
          stop_words) for sent in sentence_list]
        # stanford - ner tagger
        st_tagger = StanfordNERTagger(os.path.join(self.baseDir,
          'stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'),
                              os.path.join(self.baseDir,
                              'stanford-ner/stanford-ner.jar'))

        pos = 1
        sent_ent_list = st_tagger.tag_sents(sentence_tokens_list)
        for i, sent in enumerate(sent_ent_list):
          # add global position of each entity
          for j, elem in enumerate(sent):
            elem = (elem[0], elem[1], pos)
            pos += 1
            sent[j] = elem
          sent_ent_list[i] = sent


      else:
        # spacy
        sent_ent_list = []
        pos = 1
        for i in range(len(sentence_list)):
          sentence_list[i] = nlp(sentence_list[i])
          temp_list = []
          for word in sentence_list[i]:
            temp_list.append((word.text, word.ent_type_, pos))
            pos += 1
          sent_ent_list.append(temp_list)
      # expected return type - dict containg the primary entities
      # of each type - LOC, ORG, PER with the these specific key names
      print("TIME BEFORE CUSTOM FUNC: %s" %(time.time() - t1))
      custom_relev_entities = self.custom_entity_detect_func(sent_ent_list,
                              sentence_list, content, self.custom_param)

      t1 = time.time()
      self.evaluate(custom_relev_entities, json_dict, sent_ent_list)
      print("TIME TO EVALUATE: %s" %(time.time() - t1))


  # Measure the precision, recall and f1 for the given file
  def evaluate(self, custom_relev_entities, json_dict, sent_ent_list):
    # Format of relevant entities as marked in the tagged json files
      json_format = {
            "LOC"   : "Event",
            "ORG"   : "Accused",
            "PER"   : "Accused",
      }

      if self.eval_NER:
        ner_entities = get_all_entities(sent_ent_list)
      
      for ent_type in json_format.keys():
        relev_ent = []
        for ent in json_dict[ent_type]:
          if ent[2] == json_format[ent_type]:
            # convert to lower
            relev_ent.append(ent[0].lower())

        relev_ent = set(relev_ent)
        # Evaluates the custom function on the restricted set
        # of entities - the ground truth/tagged relevant entities
        # intersection with the NER entities to better understand
        # the shortcomings of the custom function
        if self.eval_NER:
          relev_ent = relev_ent.intersection(ner_entities[ent_type])

        temp_set = set([ent.lower() for ent in custom_relev_entities[ent_type]])
        common = len(relev_ent.intersection(temp_set))
        print (ent_type, relev_ent, temp_set)
        # CHECK IF PRECISION hsould be 1 or 0 in the edge case
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
