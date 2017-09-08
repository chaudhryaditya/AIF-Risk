#Sentence Matching
#Jeevan Karamsetty & Han Gu 
#AIF Risk

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pickle as cPickle 
import editdistance
from os import listdir
from os.path import isfile, join


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


from pprint import pprint
def computeNumDifferences(filename1,filename2):
	# listOne= ['Aditya is a scum', 'The cat ate the dog', 'Han is a first year', 'Katy Perry ate the cat']
	# listTwo= ['Jeevan is a second year', 'Aditya is a scum', 'The cat ate the cat']


	numChanges=0
	# print(filename1)
	dictOne = cPickle.load(open(filename1, "rb"))


	try:
		listOne = dictOne['Risk Factors'].split('.')
	except:
		return -1


	dictTwo= cPickle.load(open(filename2, "rb"))
	

	try:
		listTwo = dictTwo['Risk Factors'].split('.')
	except:
		return -1


	# pprint(listTwo)

	# print('LETS FUCKIGN GO')
	outputname=filename1+"matcher.txt"
	# text_file=open(outputname,"w")

	listOneCount = 0 

	sentCount = 0 
	
	for sentenceOne in listOne:

		sentCount = sentCount + 1
		# print(sentCount)

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

		# if(max==100):
		# 	text_file.write(listOne[listOneCount]+"is the same as"+listTwo[listTwoBestCount]+ "\n")

		# else:
			# text_file.write('SENT 1: ' + listOne[listOneCount] + "\n")
			# text_file.write('is most similar to'+ "\n")
			# text_file.write('SENT 2: '+ listTwo[listTwoBestCount]+ "\n")
			# text_file.write("the benchmark is"+ str(max)+ "\n")
			# text_file.write("words matched "+ str(dups[0])+ "\n")	
			# text_file.write("unique to sentence one "+ str(dups[1])+ "\n")
			# text_file.write("unique to sentence two "+ str(dups[2])+ "\n")
		numChanges=numChanges+editdistance.eval(listOne[listOneCount], listTwo[listTwoBestCount])


		listOneCount+=1
	# 	text_file.write(""+ "\n")
	# text_file.close()
	return numChanges	

import pandas as pd
import pandas_datareader.data as web



# In[2]:

def get_returns(ticker, start_date, end_date):
    start_date = start_date
    df = web.DataReader(ticker, 'yahoo', start_date, end_date)
    df = df[['Adj Close']]
    df.columns = ['Adj_Close']
    df = df.Adj_Close.pct_change().to_frame()
    return df


def get_percent_change(ticker, start_date, end_date):

	start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
	end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

	print(start_date)
	print(end_date)

	# print(ticker)
	df = web.DataReader(ticker, 'yahoo', start_date, end_date)
	df = df[['Adj Close']]
	df.columns = ['Adj_Close']


	priceOnStartDate = float(df.iloc[0])
	priceOnEndDate = float(df.iloc[-1])

	return (priceOnEndDate - priceOnStartDate) / priceOnStartDate

#"A_10k_GOOG_year_releasedate"


import datetime
import sys 

timeHorizon = 120 #in days (~20 days per month)

if __name__ == "__main__":
	numChangesList=[]

	all10KsDirName = "Pickles/"

	listOfFolderNamesForAllPickleFiles = [folder_name for folder_name in listdir(all10KsDirName) if folder_name.find('.') <= -1]


	dictOf10K_to_textChanges_to_priceChanges = {}

	for folder in listOfFolderNamesForAllPickleFiles:
	    #ticker name is file
	    pickleFolderPath = all10KsDirName + folder + "/"

	    listOfPickleFilesForThisTicker = sorted([pickleFolderPath + file_name  for file_name in listdir(pickleFolderPath) ])


	    for fileIndex in range(len(listOfPickleFilesForThisTicker) - 1):

	    	# try:
	    	firstPickleFileName = listOfPickleFilesForThisTicker[fileIndex] #previous year
	    	secondPickleFileName = listOfPickleFilesForThisTicker[fileIndex + 1] #this year

	    	# print(firstPickleFileName)

	    	ticker = secondPickleFileName[ secondPickleFileName.rfind('/') + 1 : secondPickleFileName.find('_')]

	    	print(ticker)
	    	current_date_string = secondPickleFileName[ secondPickleFileName.rfind('_') + 1 : secondPickleFileName.find('.') ]
	    	# print(current_date_string)
# 
	    	# print(current_date_string)

	    	currentDate_datetime = datetime.datetime.strptime(current_date_string, "%Y-%m-%d")

	    	print(current_date_string)

	    	end_date = currentDate_datetime + datetime.timedelta(days = timeHorizon)

	    	end_date_string = end_date.strftime('%Y-%m-%d')

	    	# print(end_date_string)


	    	# try:

    		numDiffsForThisCombo = computeNumDifferences(secondPickleFileName,firstPickleFileName) #compute # diffs btw this year and last year's 10Ks

    		if numDiffsForThisCombo < 0:
    			continue
	    	# except:
	    	# 	continue

	    	# print(numDiffsForThisCombo)



	    	try:
	    		princeChange = get_percent_change(ticker, current_date_string, end_date_string)
	    	except:
	    		break



	    	dictOf10K_to_textChanges_to_priceChanges[secondPickleFileName] = [numDiffsForThisCombo, princeChange]

	    	# except:
		    # 	continue

	cPickle.dump(dictOf10K_to_textChanges_to_priceChanges, open("finalfile.p", 'wb')) 
	print(dictOf10K_to_textChanges_to_priceChanges)




