** Journal:

*** Entry 1: 1a904a264
**Oct 25:** We tried to naive way to generate keywords. Given a radius r, for each file in the training data set, for each Relevant entity, we look at r words on either side(which are not stopwords) and add them to a counter. The top n words(where n is the threshold) becomes our keyword set.

For `n = 10`, we got very relevant keywords, like *'blast'*, *'suspect'*, *'bomb'*, *'police'*, which seemed like it could improve precision, but on experimaentation, it gave a precision of `0.4 - 0.5`, and a recall of `0.9+`, on varying radius while detecting entities.

Some the keywords are very general for the corpus, and hence the high recall and low precison. So non-relev entities are chosen very often.

Excerpt:
1. 019_007: "The West Bengal unit of the BJP is blaming Chief Minister Mamata Banerjee for blocking a probe by the National Investigation Agency -LRB- NIA -RRB- into last Thursdays blast in Bardhaman ."

2. 014_003: "National Congress , Left condemn Assam blast . . By Our Special Correspondent . . NEW DELHI , AUG. 16 . The Congress and the Left Parties today expressed deep shock over the killing of 13 persons , mostly schoolchildren , at an Independence Day parade by militants at Dhemaji in Assam ."

3. 063_020: "The Security Council condemns in the strongest terms the series of bomb attacks that occurred in different parts of India , including Mumbai , on 11 July 2006 , '"

Img 1_a depicts how many non-relevant entities also have so recogonized keywords near them.

--------------------------------------------



