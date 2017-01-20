'''
This code provides a simple example of matching sentences across 10-Ks
------------------------------------------------------------------------


YOU NEED TO INSTALL SPACY: see https://spacy.io/docs/usage/

All you need to do is type these two commands into terminal:

pip install -U spacy

python -m spacy.en.download all

------------------------------------------------------------------------

YOU NEED TO INSTALL fuzzy-wuzzy: see https://spacy.io/docs/usage/

All you need to do is type these two commands into terminal:

pip install fuzzywuzzy 

pip install python-Levenshtein
'''


from fuzzywuzzy import process
from pprint import pprint
import string


#2016 sentences
s1 = 'Global and regional economic conditions could materially adversely affect the Company.'

s2 = 'Global markets for the Company’s products and services are highly competitive and subject to rapid technological change, and the Company may be unable to compete effectively in these markets.'


#2015 sentences
s3 = 'Global and regional economic conditions could materially adversely affect the Company.'

s4 = 'Global markets for the Companys products and services are highly competitive and subject to rapid technological change, and the Company may be unable to compete effectively in these markets.'


sents_2016 = [s1, s2]
sents_2015 = [s3, s4]


#Code to remove punctuation from sentences
# table = str.maketrans({key: None for key in string.punctuation})

# sents_2016 = [	s.translate(table)     for s in sents_2016]
# sents_2015 = [	s.translate(table)     for s in sents_2015]


#MATCH USING FUZZY STRING MATCHING



dictOfSetencesMatches = {} #{sentence from 2016 : sentence from 2016 that is the closes match}

for sent in sents_2016:
	closest_sent = process.extract(sent, sents_2015, limit = 1) #extract sentence from previous year that is closest to sent

	dictOfSetencesMatches[sent] = str(closest_sent[0][0])




print(dictOfSetencesMatches)


