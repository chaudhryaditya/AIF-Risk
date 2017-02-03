# See: https://www.r-bloggers.com/modelling-dependence-with-copulas-in-r/ for refference

library('fitdistrplus')
library('compositions')
library('plot3D')
library('quantmod')
library('VineCopula')
library('copula')

getPercentChangesByYear <- function(symbol, startYear)
{
  
  allData = getSymbols.yahoo(symbol, auto.assign=FALSE)
  
  
  
  relevantColumn = names(allData)[length(names(allData))]
  values = allData[,relevantColumn]
  values = values[paste(startYear, '::')]
  
  
  percentChanges = dailyReturn(values)
  
  
  return(percentChanges)
}


getPercentChanges <- function(symbol)
{
  
  allData = getSymbols.yahoo(symbol, auto.assign=FALSE)
  
  
  
  relevantColumn = names(allData)[length(names(allData))]
  values = allData[,relevantColumn]
  values = values['2010::']
  
  
  percentChanges = dailyReturn(values)
  
  
  return(percentChanges)
}

getBestTDistDegreesOfFreedom <- function(vectorOfValues)
{
  vectorOfValues = scale(vectorOfValues)#(vectorOfValues - mean(vectorOfValues)) / sd(vectorOfValues)
  
  result = fitdistr(vectorOfValues, "t")
  bestDegreesOfFreedom = result$estimate[3]
  
  return (bestDegreesOfFreedom)
  
  
}

getMarginalDensity <- function(copula_dist, indexOfVariableWeWantMargDistFor, vectorOfValuesToConditionOn)
{
  #vectorOfValuesToConditionOn has 0 at indexOfVariableWeWantMargDistFor (in addition to possibly zeroes elsewhere as well)
  
  conditionalPDF = c()
  
  xVals = seq(-10, 10, .01)
  for(value in xVals)
  {
    thisPoint = vectorOfValuesToConditionOn
    thisPoint[indexOfVariableWeWantMargDistFor] = value
    
    densityAtThisPoint = dMvdc(thisPoint, copula_dist, log = FALSE)
    
    conditionalPDF = c(conditionalPDF, densityAtThisPoint)
  }
  
  conditionalPDF = conditionalPDF / sum(conditionalPDF)
  
  return ( list ( v1 = xVals, v2 = conditionalPDF   ) )
  
}

inverseCDF <- function(pdfVector, pdfXValues,  totalArea)
{
  
  endIndex = length(pdfVector)
  for(index in 1:length(pdfVector))
  {
    if( sum( pdfVector[ index : endIndex] ) < totalArea)
      return(pdfXValues[index])
  }
  
}
#Get all data

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

portfolioPrices = read.csv("portfolioPrices.csv")
portfolioPrices = portfolioPrices[complete.cases(portfolioPrices), ]
portfolioPrices = portfolioPrices[order( as.Date(portfolioPrices[,1], format = "%m/%d/%Y") ),  ]

betterDates <- as.Date(portfolioPrices$Date, "%m/%d/%y")

rownames(portfolioPrices) <- betterDates

portfolioPrices = subset(portfolioPrices, ,2)


portfolioChanges = data.frame(diff(as.matrix(portfolioPrices)))/portfolioPrices[-nrow(portfolioPrices),]


portfolioChanges = as.xts(portfolioChanges)


HYZD = getPercentChanges('HYZD')
SAVE = getPercentChanges('SAVE') 
SKX = getPercentChanges('SKX') 


GSPC = getPercentChanges('^GSPC') #oil etf
USO = getPercentChanges('USO') #oil etf
XLY = getPercentChanges('XLY') #consumer discretionary etf
UUP = getPercentChanges('UUP') #interest rates etf


# Need to do this if using the read in portoflio prices
indexClass(USO) <- "Date"
index(USO) <- strptime(index(USO), "%Y-%m-%d")
indexClass(XLY) <- "Date"
index(XLY) <- strptime(index(XLY), "%Y-%m-%d")
indexClassUUP <- "Date"
index(UUP) <- strptime(index(UUP), "%Y-%m-%d")
indexClassGSPC<- "Date"
index(GSPC) <- strptime(index(GSPC), "%Y-%m-%d")

allData = as.matrix(cbind(portfolioChanges, GSPC, UUP))
allData = allData[complete.cases(allData),]
namesList = c('Portfolio' , "GSPC")

vectorOfConditionalValues = c(0, -.05)

origCorr = cor(allData)

#Select copula
u <- pobs(allData)[,1]
v <- pobs(allData)[,2]
selectedCopula <- BiCopSelect(u,v,familyset=NA)
selectedCopula

#Fit copula

cop <- claytonCopula(dim = dim(allData)[2])
pseudoObs <- pobs(allData)
fit <- fitCopula(cop, pseudoObs, method='ml')
coef(fit)

#For Clayton coula
claytonParam <- coef(fit)[1]


#For t-copula
# rho <- coef(fit)[1]
# df <- coef(fit)[2]

#Plot copula density (for kicks) (2D only)
# persp(tCopula(dim = 2,rho,df=df),dCopula)

persp(claytonCopula(dim = dim(allData)[2], param = claytonParam), dCopula)


#Build copula
u <- rCopula(3965, claytonCopula(dim = dim(allData)[2], param = claytonParam))

# u <- rCopula(3965, tCopula(dim = dim(allData)[2],rho,df=df))
plot(u[,1],u[,2],pch='.',col='blue') # (2D only)
cor(u,method='spearman') #Should be close to origCorr

#Get marginal distributions
means = colMeans(allData)
stdDevs =  apply(allData, 2, sd)

listOfDegreesOfFreedom = matrix(0, nrow = ncol(allData))

for( index in 1 : length(listOfDegreesOfFreedom))
{
  listOfDegreesOfFreedom[index] = getBestTDistDegreesOfFreedom(as.matrix(allData[,index])) 
  
}

standardizedAllData = scale(allData)

#Visualize fit
for( index in 1 : length(listOfDegreesOfFreedom))
{
  hist(standardizedAllData[,index],breaks=80,main=namesList[index],freq=F,density=30,col='cyan', xlim = c(-4, 4) )
  lines(seq(-4, 4, .1),dt(seq(-4, 4, .1), listOfDegreesOfFreedom[index]),col='red',lwd=2)
  
  legend('topright',paste('Fitted T(', toString(listOfDegreesOfFreedom[index]) , ')' ),col=c('red'),lwd=2)
}

#Now apply copula
paramList = list()
for( index in 1 : length(listOfDegreesOfFreedom))
{
  paramList = list(paramList, list(df = listOfDegreesOfFreedom[index]))
  
}

marginalsList = c()

for(index in 1:(dim(allData)[2]))
{
  marginalsList = c(marginalsList, "t")
}

paramMarginsList = c()

for(index in 1:(dim(allData)[2]))
{
  paramMarginsList = c(paramMarginsList, list(df = listOfDegreesOfFreedom[index]))
}


# copula_dist <- mvdc(copula=tCopula(rho , dim = dim(allData)[2] , df=df), margins = marginalsList,
#                     paramMargins=paramMarginsList )

copula_dist <- mvdc(copula = claytonCopula(dim = dim(allData)[2], param = claytonParam), margins = marginalsList,
                    paramMargins=paramMarginsList )
sim <- rMvdc(1000, copula_dist)

#Visualize final fit (2D only)

plot(standardizedAllData[,1],standardizedAllData[,2],main='Returns')
points(sim[,1],sim[,2],col='red')
legend('bottomright',c('Observed','Simulated'),col=c('black','red'),pch=21)



#3D Dist plot (CAN ONLY DO FOR 2 VARIABLES)

indexOfFirstVariable = 1
indexOfSecondVariable = 2


xVals = seq(min(standardizedAllData[,indexOfFirstVariable]), max(standardizedAllData[,indexOfFirstVariable]), (max(standardizedAllData[,indexOfFirstVariable]) - min(standardizedAllData[,indexOfFirstVariable])) / 50)
yVals = seq(min(standardizedAllData[,indexOfSecondVariable]), max(standardizedAllData[,indexOfSecondVariable]), (max(standardizedAllData[,indexOfSecondVariable]) - min(standardizedAllData[,indexOfSecondVariable])) / 50)


densities = matrix(0 , nrow = length(xVals), ncol = length(yVals))

for (xIndex in 1:length(xVals))
{
  for(yIndex in 1:length(yVals))
  {
    xVal = xVals[xIndex]
    yVal = yVals[yIndex]
    
    densities[xIndex, yIndex] =  dMvdc(c(xVal, yVal), copula_dist, log = FALSE)
  }
  
}

xVals = xVals * stdDevs[1] + means[1]
yVals = yVals * stdDevs[2] + means[2]

persp3D(xVals, yVals, densities, phi = 30, theta = 30, ticktype = "detailed",
        xlab = paste("\n", namesList[1]), ylab = paste("\n", namesList[2]), zlab = "\n\nProbability",
        facets = FALSE, plot = FALSE)



#3D conditional distribution
conditionalValue = vectorOfConditionalValues[2]
newYVals = yVals
for(index in 1:length(yVals))
{
  newYVals[index] = conditionalValue
}
newXVals = xVals
zVals = .1#matrix(.1, ncol = 2,  nrow = length(yVals))[,1]
image3D(newXVals, conditionalValue, z = range(0, .1, .01), add = TRUE, col = 'red', facets = TRUE, plot = TRUE, alpha = .5)

#Plot conditional distribution

standardizedConditionalValues = (vectorOfConditionalValues - means) / stdDevs


standardizedConditionalValues[1] = 0 #Dependent variable needs value of 0


l <- getMarginalDensity(copula_dist, 1, standardizedConditionalValues )

standardizedConditionalXValues = l[[1]]
conditionalDist = l[[2]]

conditionalXValues = standardizedConditionalXValues * stdDevs[1] + means[1]

portfolio.hist <- hist(allData[,1], plot=FALSE, breaks = length(conditionalXValues))
portfolio.hist$counts <- portfolio.hist$counts/sum(portfolio.hist$counts)
plot(portfolio.hist, col = 'cyan',  main = namesList[1], xlab = namesList[1], ylab = 'Probability')
lines(conditionalXValues , conditionalDist ,col='red',lwd=2)


#Get Conditional VaR

unconditionalVaR = inverseCDF(portfolio.hist$counts, portfolio.hist$mids,  .95)
conditionalVaR = inverseCDF(conditionalDist, conditionalXValues,  .95)

simulatedPortfolioValue = matrix(1, nrow = 1000)
for(day in 1:30)
{
  #randomChanges =   sample(x= portfolio.hist$mids, size=1000, replace=TRUE, prob=portfolio.hist$counts)
  randomChanges = sample(x= seq(-4, 4, .1), size=1000, replace=TRUE, prob=dt(seq(-4, 4, .1), listOfDegreesOfFreedom[1])) * stdDevs[1] + means[1]
  simulatedPortfolioValue = simulatedPortfolioValue * ( 1 + randomChanges)
  print(day)
  
}


monthlyVaR = sort(simulatedPortfolioValue)[1000 * .05]
monthlyVaR - 1


#Put portfolio through 2008

stressFactors = matrix(NA, ncol = dim(allData)[2], nrow = 200) #Num rows won't be more than 200

for(index in 1:dim(allData)[2])
{
  valuesForThisAsset = getPercentChangesByYear(namesList[index], '2008-09-01')
  valuesForThisAsset = valuesForThisAsset['::2009-03-01']
  stressFactors[1:length(valuesForThisAsset) , index] = valuesForThisAsset
  
  
}

stressFactors = stressFactors[complete.cases(stressFactors),]


portfolioValue = matrix(1, nrow = 1000)
listOfPortfolioValues = c()

for (index in 1:length(stressFactors))
{
  
  conditionalValueVector = stressFactors[index,]
  standardizedConditionalValues = (conditionalValueVector - means) / stdDevs
  standardizedConditionalValues[1] = 0
  
  l <- getMarginalDensity(copula_dist, 1, standardizedConditionalValues )
  
  standardizedConditionalXValues = l[[1]]
  conditionalDist = l[[2]]
  
  conditionalXValues = standardizedConditionalXValues * stdDevs[1] + means[1]
  
  portfolio.hist <- hist(allData[,1], plot=FALSE, breaks = length(conditionalXValues))
  portfolio.hist$counts <- portfolio.hist$counts/sum(portfolio.hist$counts)
  
  randomChanges = sample(conditionalXValues, size = 1000, prob = conditionalDist)
  portfolioValue = portfolioValue * ( 1 + randomChanges)
  print(index)
  
}

stressTestVaR = sort(portfolioValue)[1000 * .05]
stressTestVaR - 1
hist(sort(portfolioValue)[0:950], breaks = 100, xlim = c(0, max(sort(portfolioValue)[0:950])), col = 'cyan', density = 30)
abline(v = stressTestVaR, col = 'red', lwd = 2)