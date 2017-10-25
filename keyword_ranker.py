import naive_gen_keywords

from collections import Counter

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from Entity_test import Tester, get_all_entities
from naive_gen_keywords import get_close_words

lemmatizer = WordNetLemmatizer()

keywords_set = [ "killed", "attacked", "shot", "injured", "suspected",
        	 "dead", "death", "exploded", "blast", "detonated", "perished" ]
keywords_set = set([lemmatizer.lemmatize(word, pos="v") for word in keywords_set])


gen_type =  {
            "Naive" : naive_gen_keywords,
            }

# Identify the primary sentences based on the presence of 
# keywords and then return the entities by category in those sentences
def keyword_ranker(sent_ent_list, sentence_list, content,
        custom_param):

  relev_ents = {
                    "LOC" : [],
                    "ORG" : [],
                    "PER" : [],
                }

  kw_type = custom_param.get("Gen_type","Naive")

  keywords = set()
  if "default_type":
      keywords = {
                  "LOC"   :   keywords_set,
                  "ORG"   :   keywords_set,
                  "PER"   :   keywords_set,
      }
  else:
      keywords = gen_type(kw_type).gen_keywords(
          custom_param.get("Gen_param", {}))
  tokenized_string = word_tokenize(content)
  tokenized_string = [word.lower() for word in tokenized_string]

  all_ents = get_all_entities(sent_ent_list, True)

  for ent_type in all_ents.keys():
    for ent, ln_no, pos in all_ents[ent_type]:
      relev_entity = {
                      ent_type : [],
                     }
      relev_entity[ent_type].append((ent, pos))
      close_ = { 
              ent_type   :   Counter(),
            }
      get_close_words(tokenized_string, relev_entity, close_,
        # check this line
        4)
      close_set = set(close_[ent_type].keys())
      if not close_set.intersection(keywords[ent_type]):
        relev_ents[ent_type].append(ent)

  return relev_ents


def main():
    tester = Tester(keyword_ranker, size=10, stop=False,)
    tester.test()
    tester.score(True)

if __name__ == "__main__":
	main()
