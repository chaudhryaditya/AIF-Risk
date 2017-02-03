#Sentence Matching
#Jeevan Karamsetty & Han Gu 
#AIF Risk

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pickle 


def convertSentenceToHashMap(x1):

	mapOne= {} 
	for word in x1:
		word.lower() #put all words in lowercase
		if(word not in mapOne): #Make a map with individual words as keys that point to an integer of their frequency
			mapOne[word]= 1
		else:
			mapOne[word]+= 1
	return mapOne

def benchmark(mapOne, mapTwo):
	duplicates= []
	sentenceOneUnique= []
	sentenceTwoUnique= []
	
	for key in mapOne: #Return the sum of the number of word matches between two sentences.
		if(key in mapTwo): 
			duplicates.append(key)
		else:
			sentenceOneUnique.append(key)

	for key in mapTwo:
		if key not in mapOne:
			sentenceTwoUnique.append(key)

	return duplicates, sentenceOneUnique, sentenceTwoUnique


def main():
	# listOne= ['Aditya is a scum', 'The cat ate the dog', 'Han is a first year', 'Katy Perry ate the cat']
	# listTwo= ['Jeevan is a second year', 'Aditya is a scum', 'The cat ate the cat']

	dict_2015 = pickle.load(open("2015dict.p", "rb"))
	dict_2016= pickle.load(open("2016dict.p", "rb"))

	listOne= dict_2015["Item 3"].split(".")
	listTwo= dict_2016["Item 3"].split(".")

	listOneCount = 0 
	for sentenceOne in listOne:
		dups= []
		max= 0.0
		listTwoCount= 0
		listTwoBestCount = 0
		for sentenceTwo in listTwo: 
			result = fuzz.ratio(sentenceOne, sentenceTwo)
			if(result>max):
				max= result
				listTwoBestCount= listTwoCount
				dups= benchmark(convertSentenceToHashMap(sentenceOne.split()), convertSentenceToHashMap(sentenceTwo.split()))
			listTwoCount+=1

		if(max==100):
			continue
			# print(listOne[listOneCount],"is the same as", listTwo[listTwoBestCount])

		else:
			print('SENT 1: ' , listOne[listOneCount])
			print('is most similar to')
			print('SENT 2: ', listTwo[listTwoBestCount])
			print("the benchmark is", max)
			print("words matched ", dups[0])	
			print("unique to sentence one ", dups[1])
			print("unique to sentence two ", dups[2])
		listOneCount+=1
		print("")		


if __name__ == "__main__":
    main()