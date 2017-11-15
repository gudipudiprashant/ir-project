import json

def resolve_coref(coref_list, sent_token_list):
  word_coref_list = []
  for coref_chain in coref_list:
    
    temp_list = []
    for phrase_dict in coref_chain:
      word = ""
      sent_num = phrase_dict["sentnum"]
      for ii in range(phrase_dict["startindex"], phrase_dict["endindex"]+1):
        word += sent_token_list[sent_num][ii][0] + " "
      word = word.strip()
      temp_list.append(word.lower())
    
    word_coref_list.append(temp_list)
  return word_coref_list

# Returns the list of sentences
def make_proper_sent_tokens_list(sent_token_list):
  sent_list = []
  pos_ctr = 1
  for sent in sent_token_list:
    temp_list = []
    for i, word_dict in enumerate(sent):
      sent[i] = (word_dict["tokentext"], word_dict.get("netype", "O"), pos_ctr)
      pos_ctr += 1
      temp_list.append(sent[i][0])
    sent_list.append(temp_list)
  return sent_list

# returns list of sentences, sentence entities and coref-chains
def get_sent_token_coref(filename):
  json_dict = json.load(open(filename, "r", encoding="utf-8"))
  sentence_list = make_proper_sent_tokens_list(json_dict["ner"])
  coref_list_res = resolve_coref(json_dict["coref"], json_dict["ner"])
  return sentence_list, json_dict["ner"], coref_list_res


def main():

  sent_token_list, coref_list = get_sent_token_coref("out/ev_001_st_007.jsn.json")
  sentence_list = make_proper_sent_tokens_list(sent_token_list)
  for sent in sent_token_list:
    print(sent)
  coref_list_res = resolve_coref(coref_list, sent_token_list)
  for coref_chain in coref_list_res:
    print(coref_chain)

if __name__ == "__main__":
  main()