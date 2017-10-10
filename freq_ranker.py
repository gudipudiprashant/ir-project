def freq_ranker(sent_ent_list, sentence_list, content):
	ent_counter = {
		"LOC": {},
		"PER": {},
		"ORG": {},
	}

	for sent_entities in sent_ent_list:
		# Get entites for each sentence
		for entity_tup in sent_entities:
			name, ent_type, pos = entity_tup
			if name in ent_counter[ent_type]:
				ent_counter[ent_type][name] += 1
			else:
				ent_counter[ent_type][name] = 0

	prim_ent_dict = {
		"LOC": [],
		"PER": [],
		"ORG": [],
	}

	for ent_type in ent_counter:
		max_count = max([ent_counter[ent_type][key] for key in ent_counter[ent_type]])
		# Putting threshold at max_freq/2 for now. This decides
		# Which entites are primary for now
		threshold = int(max_count / 2)
		for entity in ent_counter[ent_type]:
			if ent_counter[ent_type][entity] >= threshold:
				prim_ent_dict[ent_type].append(entity)

	return prim_ent_dict