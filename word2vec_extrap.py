# Extrapolate the current keywords using word2vec similarity.
# 0. While levels < LEVEL_Threshold
# 1. Given a set of seed keywords, for each word
# 2. Generate similar keywords into a counter C
# 3. Calculate the score based on the count. Score = 1/seed_count * freq. Currently this does not depend on the score of the seed word.
# 4. Add the seed keywords to the global keyword set
# 5. For keywords allready in global set, add the score to the global 
# 5. For scores below threshold in C, discard
# 6. The Seed keyword set is all the remaining words in C
# 7. Goto 0

from collections import Counter
# For each word, also store the score
default_seed_set =  set([ "killed", "attacked", "shot", "injured", "suspected",
        	 "dead", "death", "exploded", "blast", "detonated", "perished" ])

class W2vExtrapolator:
	def __init__(self, ent_set, seed_set = default_seed_set):
		self.seed_set = seed_set
		self.ent_set = ent_set

	def extrapolate(self, levels = 2, keyword_thresh = 0.5):
		keyword_set = {}
		seed_set = self.seed_set
		for word in seed_set:
			keyword_set[word] = 1
		# score = 1 # Starting at lvl 0
		for lvl in range(levels):
			seed_count = len(seed_set)
			sim_list = []
			for word in seed_set:
				sim_list += list(self.gen_similar(word, 5))
			sim_counter = Counter(sim_list) # Counter of similar words
			seed_set = set()
			for word in sim_counter:
				word_score = sim_counter[word] / seed_count
				if word not in keyword_set:
					keyword_set[word] = 0
					if word_score >= keyword_thres:
						seed_set.add(word)
				keyword_set[word] = max(1, keyword_set[word] + word_score)
		return keyword_set
		
	# Given a word, use word to vec to generate similar words
	def gen_similar(word, top_thresh = 5):
		similar = [ ('w', 2 ) ]  # word2vec generate statement here
		non_ent_list = []
		for word_tup in similar:
			if word_tup[0] not in self.entitiy_set:
				non_ent_list.append(word_tup)

		similar = sorted(non_ent_list, key = lambda x: x[1])
		return set(similar[:top_thresh])

