from collections import Counter
from Entity_test import Tester, get_all_entities

keywords = set([ "killed", "attacked", "shot", "injured", "suspected",
        	 "dead", "death", "exploded", "blast", "detonated", "perished" ])

# Identify the primary sentences based on the presence of 
# keywords and then return the entities by category in those sentences
def keyword_ranker(sent_ent_list, sentence_list, content,
 		custom_param):
	# First identify primary sentences
	primary_sents = []
	for sent_num, sent_ents in enumerate(sent_ent_list):
		for ent in sent_ents:
			if ent[0] in keywords:
				primary_sents.append(sent_num)
				break

	relev_ents = {
                    "LOC" : [],
                    "ORG" : [],
                    "PER" : [],
                 }
  	all_ents = get_all_entities(sent_ent_list)
  	for ent_catg in all_ents:
  		for ent in all_ents[ent_catg]:
  			if ent[1] in primary_sents:
  				relev_ents[ent_catg].append(ent[0])
  	return relev_ents


def main():
	tester = Tester(keyword_ranker, size=10, stop=False,)
	tester.test()
	tester.score(True)

if __name__ == "__main__":
	main()
