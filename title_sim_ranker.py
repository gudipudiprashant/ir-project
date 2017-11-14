from Entity_test import Tester, get_all_entities
import spacy
import time

### Requires python3 -m spacy download en_core_web_lg

## Apparently the word vectors are not shipped with spacy's default
## No wonder, the package seems to be 1 GB
## seems like it. Let's see if thats really the case.


def custom_entity_detect_func(sent_ent_list, sentence_list, content,
  custom_param):
    t1 = time.time()
    relev_entitites = {
                      "LOC": [],
                      "ORG": [],
                      "PER": [],
                      }
    mapper = {"LOCATION": "LOC", "ORGANIZATION": "ORG", "PERSON": "PER"}


    # set up the word vectors:
    nlp = custom_param["nlp_spacy"]

    #Get similarity threshold:
    threshold = custom_param.get("threshold", 0.6)
    print("threshold is: " + str(threshold))
    # input()

    #Get title
    title = custom_param.get("title")
    title_nlp = nlp(title)
    print(title)
    
    sent_count = 0
    for sentence in sentence_list:

        sentence1 = ""
        if type(sentence) != str:
            sentence1 = sentence.text
            print("sentence is not string!")
            input()
        else:
            sentence1 = sentence
        sent_nlp = nlp(sentence1)
    
        # print(sent_nlp.similarity(title_nlp))
        if sent_nlp.similarity(title_nlp) > threshold:
            ent_list = get_all_entities([sent_ent_list[sent_count]])
            for ent_type in ["LOC", "ORG", "PER"]:
                relev_entitites[ent_type] += ent_list[ent_type]
        
        sent_count += 1

    t2 = time.time()

    print(str(t2-t1))
    return relev_entitites

def main():
  tester = Tester(custom_entity_detect_func, size=1, stop=False, tagger="spacy", custom_param = {"threshold": 0.7})
  tester.test()
  tester.score(True)

if __name__ == "__main__":
  main()