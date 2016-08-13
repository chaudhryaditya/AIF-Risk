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
import csv

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

    fileName = 'allGrangerCauses.txt'

    listOfConditionalGrangerCauses = doStuff(fileName, 'SAVE')



    pprint(listOfConditionalGrangerCauses)

    labelResults(labeledFileName = 'allGrangerCausesLabeled.txt', resultsFileName  = 'conditionalGrangerCauses.txt')


    
def doStuff(name, responseVariable):


        listOfSymbolsUsedInRegression = ['INTERCEPT', responseVariable]
        
        ro.r('library("quantmod")')
        ro.r('library("tseries")')
        ro.r('library("glmnet")')
        


        responseVariablePercentChange = ro.r("rv = getPercentChanges("  + '"' + responseVariable + '"'  + ")" )

        requiredNumberOfObservations = len(responseVariablePercentChange) - 10
       


        thisFile = open(name, 'r')


        listOfSymbolsInThisFile = []


        for line in thisFile:
            line = line.strip()

            symbol = line[: line.find('\t')]
            listOfSymbolsInThisFile.append(symbol)
            #break


        ro.r('designMatrix = rv')



        #Put all data in 1 matrix
        count = 0

        for symbol in listOfSymbolsInThisFile:  #For each symbol

            if symbol == responseVariable:  #We've already added responseVariable to design matrix
                continue
            count = count + 1
            print(symbol + ', ' + str(count) + ' out of ' + str(len(listOfSymbolsInThisFile)))
            
            # if count > 100:
            #     break


            #Get the data for this symbol 
           # print('"' + symbol + '"')
            try:
                percentChanges = ro.r("possibleCause = getPercentChanges("  + '"' + symbol + '"' + ")" ) 
            except:
                print("SOMETHING WENT WRONG")
                listOfSymbolsInThisFile.remove(symbol)
                continue

       
            meanChange = float(ro.r('mean(possibleCause)')[0])

            dim = ro.r('dim(possibleCause)')
          
            if dim[0] < requiredNumberOfObservations:
                listOfSymbolsInThisFile.remove(symbol)
                continue




            #Put all data in 1 matrix
              
            ro.r('designMatrix = merge(designMatrix, possibleCause)')
           # ro.r('print(dim(possibleCause))')
            ro.r('print(dim(designMatrix))')


            listOfSymbolsUsedInRegression.append(symbol)



        #Now run Lasso Granger


        ro.r('designMatrix = designMatrix[complete.cases(designMatrix),] ')


        ro.r('responseVector = designMatrix[,1]')


        ro.r('designMatrix = lag(designMatrix, k = 1)') #Lag design matrix by 1 period
        ro.r('designMatrix = designMatrix[complete.cases(designMatrix),]') #Remove NA from top
        ro.r('responseVector = responseVector[-1,]') #Remove top observation, which we can no londer use

       
        ro.r('lassoModel = glmnet(x = designMatrix, y = responseVector, alpha = 1)') #alpha = 1 means Lasso, using default Lasso path

        ro.r('coeffs = coef(lassoModel, s = lassoModel$lambda[round(length(lassoModel$lambda)/2)])') #we pick the least amount of penalization

        ro.r('print(coeffs)')

        listOfIndiciesOfNonZeroCoeffs = ro.r('indiciesOfNonZeroCoeffs = which(coeffs != 0) - 1')    #We subtract 1 because R is 1-indexed, while Python is 0-indexed
                                                                                                 #We subtract 1 again, because we want to ignore the intercept
                                                                                                 #We subtract 1 again to igrnore the response variable in the first column
        pprint(listOfIndiciesOfNonZeroCoeffs)
        listOfConditionalGrangerCauses = []

        for index in listOfIndiciesOfNonZeroCoeffs:

            index = int(index)

            if index == 0:  #We ignore the intercept
                continue

            # if index == 2:
            #     listOfConditionalGrangerCauses.append(responseVariable)

            # else:
            listOfConditionalGrangerCauses.append(listOfSymbolsUsedInRegression[index])



        outfile = open('conditionalGrangerCauses.txt', 'w')

        for symbol in listOfConditionalGrangerCauses:
            outfile.write(symbol)
            outfile.write('\n')
        outfile.close()

        print(str(len(listOfConditionalGrangerCauses)) + ' out of ' + str(len(listOfSymbolsUsedInRegression)) + ' coefficients are non-zero') 


        print("Design Matrix Dimensions")
        ro.r('print(dim(designMatrix))')

        return listOfConditionalGrangerCauses


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
        symbol = line.strip()

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