import urllib
import re
from pprint import *
import Quandl
from  scipy.stats import *
from ystockquote import *
import numpy as np
import time
import Quandl
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

#This script pulls data from Quandl to assess Granger causality and correlation between a given response variable (can be a stock, commodity, or other financial instrument),
#and tens of thousands of other financial instruments so as to discover possible latent risks factors

#One may find output in the variaous .csv files labelled "gCause_LookAtThisStuffMoreClosely_", followed by the relevant database name

#In order to use this script, one need only change the following fields:
#   responseVarDataSet (line 45)
#   rVName (line 46)




def main():

    getPercentChanges = ro.r('''
    getPercentChanges <- function(symbol)
    {
    
        allData = getSymbols.yahoo(symbol, auto.assign=FALSE)



        relevantColumn = names(allData)[length(names(allData))]
        values = allData[,relevantColumn]
        values = values['2014::']


        percentChanges = dailyReturn(values)


        return(percentChanges)
    }''')

    #listOfFileNames = ['yahooTickerList_Stocks.csv']
    # listOfFileNames = ['yahooTickerList_Stocks.csv' ,  'yahooTickerList_Indicies.csv', 'yahooTickerList_ETFs.csv']
    # listOfOutputFiles = []

    # for name in listOfFileNames:
    #     listOfOutputFiles.append(doStuff(name, ' "SAVE" ', 200000))
 

    # # listOfOutputFiles = ['gCause_LookAtThisStuffMoreClosely_ "SAVE" LONG_yahooTickerList_Stocks.csv.txt', 'gCause_LookAtThisStuffMoreClosely_ "SAVE" LONG_yahooTickerList_Indicies.csv.txt', 'gCause_LookAtThisStuffMoreClosely_ "SAVE" LONG_yahooTickerList_ETFs.csv.txt']
    # mergeOutputFiles(listOfOutputFiles, 'allGrangerCauses.txt')
    
    labelResults(labeledFileName = 'allPotentialGrangerCausesLabeled.txt', resultsFileName  = 'allGrangerCauses.txt')

    
def doStuff(name, responseVariable, maxCount):



        
        ro.r('library("quantmod")')
        ro.r('library("tseries")')
        ro.r('library("vars")')
        


        #responseVariable = ' "SAVE" '

        responseVariablePercentChange = ro.r("rv = getPercentChanges("  + responseVariable + ")" )

        
        stuffToLookAtMoreCloselyFile = open('gCause_LookAtThisStuffMoreClosely_' + responseVariable + 'LONG_' + name + '.txt', 'w')


        thisFile = open(name, 'r')


        listOfSymbolsInThisFile = []


        for line in thisFile:
            line = line.strip()
            listOfSymbolsInThisFile.append(line)
        


        dictOfStuffToLookAtMoreClosely = {}


        numberOfDataSetsThatWorked = 0
        numberOfDataSetsThatDidntWork = 0
     


        #For each symbol, determine if it granger causes the response variable from above

        count = 0

        for symbol in listOfSymbolsInThisFile:

            count = count + 1

            if count >= maxCount:
                break

            print('Successfully ran calculations on : ' + str(numberOfDataSetsThatWorked) + ' datasets')


            print(symbol)
            
           # symbol =  '"' + symbol + '"'



            #Get the data for this symbol 
            try:
                percentChanges = ro.r("possibleCause = getPercentChanges("  + '"' + symbol + '"' + ")" ) 
              #  print(meanChange)

            except:
                numberOfDataSetsThatDidntWork += 1
                print('Call to Yahoo Finance Failed '+ str(numberOfDataSetsThatDidntWork))
                continue
           
            meanChange = float(ro.r('mean(possibleCause)')[0])

            if(meanChange == 0):
                numberOfDataSetsThatDidntWork += 1
                print('Data set is empty: '+ str(numberOfDataSetsThatDidntWork))
                continue



            #Put all data in 1 matrix

            try:
               # ro.r('minNumberOfEntries = min( length(rv), length(possibleCause) )')



                #ro.r(' possibleCause = possibleCause[(length(possibleCause) - minNumberOfEntries + 1) : length(possibleCause)] ')

                # ro.r('print(length(possibleCause))')


                # ro.r(' print(possibleCause[1])')




               # ro.r(' rv = rv[(length(rv) - minNumberOfEntries + 1) : length(rv)] ')

                # ro.r('print(length(rv))')

                # ro.r(' print(rv[1])')



                ro.r('data = merge(rv, possibleCause)')
                ro.r('data = data[complete.cases(data),] ')



            except:
                numberOfDataSetsThatDidntWork += 1
                print('Failed to merge data sets: '+ str(numberOfDataSetsThatDidntWork))
                continue


            try:

                #Select "optimal" lag using AIC


               

                lag = int(ro.r('VARselect(data, type ="none")$"selection"["AIC(n)"]')[0])

                #Fit a VAR to the data
                ro.r('model = VAR(data, p =' + str(lag) + ' , type = "none")')





                ro.r('causalityTestResults = causality(model, cause = "daily.returns.1" )')


                pValueForGranger = float(ro.r('causalityTestResults$"Granger"$"p.value"')[0])

               # print(pValueForGranger)
                print('got here')
                if pValueForGranger < .05:
                    print('Found a granger cause')
                    correl = float(ro.r('correl = cor(data, use="complete.obs", method="pearson")[2]')[0])
                    print(correl)
                    dictOfStuffToLookAtMoreClosely[symbol] = [pValueForGranger, correl]

                numberOfDataSetsThatWorked += 1
                print('Successfully ran calculations on dataset: ' + str(numberOfDataSetsThatWorked))

            except:
             

                numberOfDataSetsThatDidntWork += 1
                print('This is one of those sketchy tickers on Yahoo Finance: '+ str(numberOfDataSetsThatDidntWork))
                continue



            


        listOfStuffToLookAtMoreCloselyNames = list(dictOfStuffToLookAtMoreClosely.keys())
    
        for dataset in listOfStuffToLookAtMoreCloselyNames:
            stuffToLookAtMoreCloselyFile.write(dataset)
            stuffToLookAtMoreCloselyFile.write('\t')
            stuffToLookAtMoreCloselyFile.write(str(dictOfStuffToLookAtMoreClosely[dataset][0])) #Granger causality p-value
            stuffToLookAtMoreCloselyFile.write('\t')
            stuffToLookAtMoreCloselyFile.write(str(dictOfStuffToLookAtMoreClosely[dataset][1])) #Correlation Coefficient
            stuffToLookAtMoreCloselyFile.write('\n')
        stuffToLookAtMoreCloselyFile.close()

        return 'gCause_LookAtThisStuffMoreClosely_' + responseVariable + 'LONG_' + name + '.txt'
        
        
#allCorrelationsFile.close()

        print(str(numberOfDataSetsThatWorked) + ' out of ' + str(numberOfDataSetsThatWorked + numberOfDataSetsThatDidntWork ) + ' worked')
            
def mergeOutputFiles(listOfOutputFiles, mergedOutputFileName):

    mergedOutputFile = open(mergedOutputFileName, 'w')


    for fileName in listOfOutputFiles:
        thisFile = open(fileName, 'r')

        for line in thisFile:
            line = line.strip()
            mergedOutputFile.write(line)
            mergedOutputFile.write('\n')

        thisFile.close()

    mergedOutputFile.close()

def labelResults(labeledFileName, resultsFileName):
    labeledFile = open(labeledFileName, 'w')
    resultsFile = open(resultsFileName, 'r')
    allDataFile = open('yahooTickerList_All_Data.txt', 'r', encoding='utf-8', errors='ignore')

    #Read in labeled file
    dictOfAllData = {}

    for line in allDataFile:
        line = line.strip()
        line = line.split('\t')
        symbol = line[0]

       # print(line)
        dictOfAllData[symbol] = line[1:]


    for line in resultsFile:
        line = line.strip()

        symbol = line[: line.find('\t')]


        print(symbol)
        allDataForThisSymbol = dictOfAllData[symbol] 
   


        labeledFile.write(symbol)
        labeledFile.write('\t')


        for item in allDataForThisSymbol:
            labeledFile.write(item)
            labeledFile.write('\t')
        
        labeledFile.write('\n')


    labeledFile.close()
    resultsFile.close()
    allDataFile.close()






if __name__ == "__main__":
        start_time = time.time()
        main()
        print("--- %s seconds ---" % (time.time() - start_time))