
library("quantmod")
library("forecast")
library("tseries")
library("PerformanceAnalytics")
library("rugarch")
library("fGarch")
library("vars")
library("quantreg")
library("astsa")


confidenceIntervalForecastGivenDifferences <- function(meanForecastVector, upper95PercentForecastVector, lower95PercentForecastVector, currentValue) #pass in the forecasted differences
{
  
  numberOfForecastPeriods = length(meanForecastVector)
  
  calculatedStandardDeviationVector = (upper95PercentForecastVector - meanForecastVector) / 1.96
  
  NUM_SIMS = 10000
  
  #We want to generate NUM_SIMS many "paths" the variable can take 
  
  #Each column here represents a path the variable can take
  simulationResultsMatrix = matrix(0, nrow = numberOfForecastPeriods + 1, ncol = NUM_SIMS)
  
  simulationResultsMatrix[1,] = currentValue
  
  for(simulation in 1:NUM_SIMS) #For each simulation
  {
    for(period in 1: numberOfForecastPeriods) #Generate a forecasted path
    {
      
      randomDiffernceToAdd = rnorm(1, mean=meanForecastVector[period], sd=calculatedStandardDeviationVector[period])
      
      simulationResultsMatrix[period + 1, simulation] = simulationResultsMatrix[period , NUM_SIMS] + randomDiffernceToAdd
      
    }
    
  }
  
  confidenceInterval95PercentForEachForecastedPeriod = matrix(0, nrow = numberOfForecastPeriods , ncol = 2)
  
  
  indexOf5Percentile = round(NUM_SIMS * .05)
  indexOf95Percentile = round(NUM_SIMS * .95)
  
  for(period in 1:numberOfForecastPeriods)#Get the 5, 50, and 95 percentiles for the forecasted values of each period
  {
    
    allForecastedValuesForThisPeriod = sort(simulationResultsMatrix[period,])
    
    confidenceInterval95PercentForEachForecastedPeriod[period, 1] = allForecastedValuesForThisPeriod[indexOf5Percentile]
    confidenceInterval95PercentForEachForecastedPeriod[period, 2] = median(allForecastedValuesForThisPeriod)
    
    confidenceInterval95PercentForEachForecastedPeriod[period, 3] = allForecastedValuesForThisPeriod[indexOf95Percentile]
    
    
  }
  return (confidenceInterval95PercentForEachForecastedPeriod)
  
}




confidenceIntervalForecastGivenLogReturns <- function(meanForecastVector, upper95PercentForecastVector, lower95PercentForecastVector, currentValue) #pass in the forecasted differences
{
  
  
  
  
  numberOfForecastPeriods = length(meanForecastVector)
  
  calculatedStandardDeviationVector = (upper95PercentForecastVector - meanForecastVector) / 1.96
  NUM_SIMS = 10000
  
  #We want to generate NUM_SIMS many "paths" the variable can take 
  
  #Each column here represents a path the variable can take
  simulationResultsMatrix = matrix(0, nrow = numberOfForecastPeriods + 1, ncol = NUM_SIMS)
  
  simulationResultsMatrix[1,] = currentValue
  
  for(simulation in 1:NUM_SIMS) #For each simulation
  {
    for(period in 1: numberOfForecastPeriods   ) #Generate a forecasted path
    {
      
      randomLogReturn = rnorm(1, mean=meanForecastVector[period], sd=calculatedStandardDeviationVector[period])
      
      simulationResultsMatrix[period + 1, simulation] = simulationResultsMatrix[period , simulation]* exp(randomLogReturn)
      
    }
    
  }
  
  
  confidenceInterval95PercentForEachForecastedPeriod = matrix(0, nrow = numberOfForecastPeriods , ncol = 3)
  
  
  indexOf5Percentile = round(NUM_SIMS * .05)
  indexOf95Percentile = round(NUM_SIMS * .95)
  
  for(period in 1:numberOfForecastPeriods) #Get the 5, 50, and 95 percentiles for the forecasted values of each period
  {
    
    allForecastedValuesForThisPeriod = sort(simulationResultsMatrix[period,])
    
    confidenceInterval95PercentForEachForecastedPeriod[period, 1] = allForecastedValuesForThisPeriod[indexOf5Percentile]
    confidenceInterval95PercentForEachForecastedPeriod[period, 2] = median(allForecastedValuesForThisPeriod)
    
    confidenceInterval95PercentForEachForecastedPeriod[period, 3] = allForecastedValuesForThisPeriod[indexOf95Percentile]
    
    
  }
  return (confidenceInterval95PercentForEachForecastedPeriod)
  
}



# Vector Autoregression

#Get all data
SPX = getSymbols("^GSPC", auto.assign=FALSE, from = '2014-03-25')
SPX = SPX[,6]
SPX = as.matrix(SPX)

SAVE = getSymbols("SAVE", auto.assign=FALSE, from = '2014-03-25')
SAVE = SAVE[,6]
SAVE = as.matrix(SAVE)

USO = getSymbols("USO", auto.assign=FALSE, from = '2014-03-25')
USO = USO[,6]
USO = as.matrix(USO)

#Convert raw prices to log-returns

logreturns = c(0,0)
for (i in 1:length(SPX)-1){
  logreturns[i] = log(SPX[i+1]/SPX[i])
}
SPXL=logreturns


logreturns = c(0,0)
for (i in 1:length(SAVE)-1){
  logreturns[i] = log(SAVE[i+1]/SAVE[i])
}
SAVEL=logreturns

logreturns = c(0,0)
for (i in 1:length(USO)-1){
  logreturns[i] = log(USO[i+1]/USO[i])
}
USOL=logreturns

y=cbind(SPXL,SAVEL,USOL)


#Determine which lag to use for VAR
VARselect(y,type="both")

var <- VAR(y, p = 1, type = "both")
plot(predict(var, n.ahead = 15, ci = 0.95))

acf(diff(SPX)) 
acf(diff(SAVE)) 
acf(diff(USO)) 
pcf(diff(SPX)) 
pcf(diff(SAVE)) 
pcf(diff(USO)) 


#Generate forecasts and confidence intervals

forecastsData = predict(var, n.ahead = 15, ci = 0.95)
fanchart(forecastsData, plot.type = "single", cis = c(.8, .95), colors = c("blue", "grey"))




#Leave the preceeding whitespace in
meanForecastSAVEL = forecastsData$fcst$SAVEL[,1]
lower95ForecastSAVEL = forecastsData$fcst$SAVEL[,2]
upper95ForecastSAVEL = forecastsData$fcst$SAVEL[,3]


forecastCI = confidenceIntervalForecastGivenLogReturns(meanForecastSAVEL, upper95ForecastSAVEL, lower95ForecastSAVEL, tail(SAVE,1)[1])

plot.ts(forecastCI, plot.type = c("single")   )


