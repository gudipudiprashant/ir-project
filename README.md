# ir-project
CS-570 Information Retrieval Project  

Team Members:  
Pranjal Agrawal - 140101050  
Prashant Gudipudi - 140101051  
Sangana Abhiram - 140101065  
Sambhav Kumar Dash - 140101088

## Problem Statement:  

Extract relevant entities from an article, which is from a specific domain.
The domain chosen is terrrorist attacks.

Definitions:
------------
1.  Entity: A Person, Location, Organization, Time, Collection or domain specific terms.
2.  Relevant: Dates(event date or article date), or entities that are directly affected by or contribute to the event are relevant.

Motivation:
-----------
Some use-cases for the solution of this problem are:
1.  Article Summarization
2.  Grouping related articles.
3.  Describing the event
4.  Information retrieval of relevant articles using entity as a query.

Solution Approach:
------------------
The solution approaches taken can be broadly classified into domain-independent and domain-specific.  
1. Domain-independent:  
    1. Frequency based:  
        Here we hypothesize that the entities that occur most frequently must be relevant.  
        
        So we extract all the entities in the document, sort them based on their frequency, and extract the relevant entities according to our hypothesis. This extraction is done using a threshold parameter. All entities that have frequency greater than (max_freq / threshold) are considered relevant.  
        
        Results for various threshold values are in Journal images.
    2. Position based:  
        Here we hypothesize that the entities that occur near the top of the document must be relevant.  
        
        So we extract the relevant sentences from the document, and extract the entities from these sentences. These are the relevant entities from our hypothesis. The threshold in this case is the number of sentences from the start of the document we consider.
        
        Results for various threshold values are in Journal images.
        
    3. Freq-Position based:  
        Here we use the paper "On-line Event Detection from Web News Stream" to give scores to each entity. The hypothesis is that entities with high scores are relevant.  
        
        So we assign scores to each entity, sort entities based on the score and extract relevant entities. Entities with score greater than (max_score / th) are considered relevant.
        
        /* Insert graph for freq-pos */
        
2. Domain-specific:
    1. Expert keyword selection:  
        Relevant Entities answer the questions such as **"who is the accused?" or "Where did the blast take place" or "Who did the attack?"**.  
        
        We identify the **answers** to these questions by **searching for sentences containing the Domain-Specific Keywords like ["attack", "bomb", "blast", "injure", "kill", ...].** For this we first prepare the sentences by **lemmatizing** them to identify the keywords in their different morphological forms, and then identify all sentences containing any of these keywords. After getting these **relevant sentences**, we extract all the Named entities in these sentences as **Relevant Entities.** 
        
        The keywords for different Entity Types like Org, Person, Loc need not be the same (this idea is further explored in the next section).  
        
        /* Insert results */  
    
    2. Unsupervised Keyword Generation:   
        Using the train data, we find the most frequently occuring words around the Relevant Entites, within a radius **r** (here 5), for each of the different categories of Named Entites - Per, Loc, Org. We then choose the **top 10** of the most frequently occuring words as the keywords of that Category.  
        
        Examples for different categories include:  
         Location:      ["blast", "bomb", "injure", "near"]  
         Organization:  ["blast", "suspect", "trigger", "militants"]  
         Person:        ["identify", "arrest", "alias", "accuse"]  
         
        We then use these keywords to identify Relevant Entities by checking if any of these keywords occur within a radius of **r** withing a Named Entity. Again we use *lemmatization* and *removal of stop words* for both the keyword generation and for Relevant Entity identification.  
         
         /* Insert Results */  
         Problem Identified: Very poor recall
         


Evaluation:
-----------
The "ground-truth" entities must describe the event, not necessarily help in recognition. They must also satisfy the above "relevant" and "entity" definitions.
