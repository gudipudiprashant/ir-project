
# Import the file containing your function
import copy
import json
import os

from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize

baseDir = "E:\College\IR\Entity"
jsonDir = "tagged_dataset"
jsonFiles = os.listdir(os.path.join(baseDir, jsonDir))


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



for file in jsonFiles:
  json_dict = json.load(open(os.path.join(baseDir, jsonDir, file)))
  content = json_dict["content"]

  sentence_list = sent_tokenize(content)

  # stop-words optional
  stop_words = set(stopwords.words('english'))
  # stop_words = set([])

  # stanford - ner tagger
  st_tagger = StanfordNERTagger(os.path.join(baseDir,
    'stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz'),
                        os.path.join(baseDir,
                        'stanford-ner/stanford-ner.jar'))
  sentence_tokens_list = [processSegment(sent,
    stop_words) for sent in sentence_list]

  # each element is a list containing the tuples -
  # (word, entity_type, position in text) for each sentence
  sent_ent_list = []

  ctr = 1
  for sent_tokens in sentence_tokens_list:
    classified_text = st_tagger.tag(sent_tokens)
    # add global position of each entity
    for elem in classified_text:
      elem = (elem[0], elem[1], ctr)
      ctr += 1
    sent_ent_list.append(classified_text)

  # expected return type - dict containg the primary entities
  # of each type - LOC, ORG, PER with the these specific key names
  custom_relev_entities = custom_entity_detect_func(sent_ent_list,
                          sentence_list, content)

  # evaluate the custom function
  json_format = {
        "LOC"   : "Event",
        "ORG"   : "Accused",
        "PER"   : "Accused",
  }

  for ent_type in json_format.keys():
    relev_ent = []
    for ent in json_dict[ent_type]:
      if ent[3] == json_format[ent_type]:
        relev_ent.append(ent[1])

    relev_ent = set(relev_ent)
    temp_set = set(custom_relev_entities[ent_type])
    common = len(relev_ent.intersection(temp_set))
    
    precision = common/len(temp_set)
    recall = common/len(relev_ent)

    eval_["precision"][ent_type].append(precision)
    eval_["recall"][ent_type].append(recall)
    divisor = precision + recall
    if divisor == 0:
      divisor = 1
    eval_["f_measure"][ent_type].append(
      2*precision*recall/divisor)


for ent_type in eval_dict.keys():
  print("Entity Type: ", ent_type)
  for measure in eval_.keys():
    print("Average %s: %s", %(measure, 
      sum(eval_[measure][ent_type])/len(eval_[measure][ent_type]) 
      ))
