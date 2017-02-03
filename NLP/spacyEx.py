'''


YOU NEED TO INSTALL SPACY: see https://spacy.io/docs/usage/

All you need to do is type these two commands into terminal:

pip install -U spacy

python -m spacy.en.download all

...

You can find documentation at: https://spacy.io/
'''

import spacy

nlp = spacy.load('en') #loads spaCy's built-in parser

s1 = "Leon is scum" #a string

doc1 = nlp(s1) #passes string to spaCy for parsing

s2 = "Ansel is scum" #a string

doc2 = nlp(s2) #passes string to spaCy for parsing

cosineSimilarity = doc1.similarity(doc2) #calculates cosine similarity of two strings


#CODE TO GET MOST SIMILAR WORDS IN THE ENTIRE VOCABULARY

def most_similar(word):
	queries = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= -15]
	by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
	return [w.lower_ for w in by_similarity[:10]]

targetString = 'scum'


mostSimilarWords = most_similar(nlp.vocab['scum'])

print(mostSimilarWords)

