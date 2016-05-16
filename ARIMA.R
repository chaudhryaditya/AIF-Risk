library("quantmod")
library("forecast")
library("tseries")
library("PerformanceAnalytics")
library("rugarch")
library("fGarch")
library("vars")
library("quantreg")
library("astsa")

# Done first using auto.arima() function

allData = getSymbols("^GSPC", auto.assign=FALSE, from = '2014-03-25')
plot(allData[,6]) #Plot adjusted prices

prices = allData[,6]
prices = as.matrix(prices)
ARIMAfit1 <- auto.arima(prices,d=1) #Differenced once, as resulted by KPSS test
ARIMAfit1
plot(forecast(ARIMAfit1,h=30)) #Forecast for 200 days using (0,1,0) model
#ARIMA(0,1,0): Difference of one, lag for AR and MA are both zero

ARIMAfit2 <- auto.arima(OilPrices, d=2) #Differenced twice
ARIMAfit2
plot(forecast(ARIMAfit2,h=30)) #Forecast for 200 days using (5,2,1) model
#ARIMA(5,2,1): Difference of 2, lag for AR is 5, lag for MA is 1





# Now done "by hand"

allData = getSymbols("^GSPC", auto.assign=FALSE, from = '2014-03-25', to = '2016-03-25')
plot(allData[,6]) #Plot adjusted prices

prices = allData[,6]

pricesDiff1=diff(prices,differences=1) #Once-diff
pricesDiff1 = pricesDiff1[2:nrow(pricesDiff1)] #get rid of now useless observation 1
plot.ts(pricesDiff1)

adf.test(pricesDiff1) 

#We will use the once-differenced data

acf(logreturns) 
acf(logreturns,plot=FALSE)

pacf(logreturns) # plot a partial correlogram - Never exceeds the significance bounds
pacf(logreturns,plot=FALSE)

# Passes both tests, so we will use once-differenced data with no lag for AR or MA





bestFit <- auto.arima(prices,d=1) #Differenced once, as resulted by KPSS test
bestFit
forecastResult = forecast(bestFit,h=15)
plot(forecastResult, main='S&P500 Value Forecasted 15 Days at 80% and 90% Confidence Using ARIMA', xlab='Time (From 2014-03-25 To 2016-03-25, Forecasted 30  Days Thereafter)', ylab='Value of S&P500') #Forecast for 30 days using (0,1,0) model
forecastResult$upper
forecastResult$lower



# Backtest ARIMA
boolInside80=c(0,0)
boolInside95=c(0,0)

for (i in 0:84){
  backTestData=prices[1:(length(prices)-100+i)]
  theGreatestFit = auto.arima(backTestData,d=1)
  forecastBackTest = forecast(theGreatestFit,h=15)
  upper80=forecastBackTest$upper[15,1]
  upper95=forecastBackTest$upper[15,2]
  lower80=forecastBackTest$lower[15,1]
  lower95=forecastBackTest$lower[15,2]
  if (prices[length(prices)-100+15+i]<=upper95 & lower95<=prices[length(prices)-100+15+i]){
    boolInside95[1+i]=TRUE
    if (prices[length(prices)-100+15+i]<=upper80 & lower80<=prices[length(prices)-100+15+i]){
      boolInside80[1+i]=TRUE
    } else {
      boolInside80[1+i]=FALSE
    }
  } else {
    boolInside95[1+i]=FALSE
    boolInside80[1+i]=FALSE
  }
}
sum(boolInside95==1)/length(boolInside95)
sum(boolInside80==1)/length(boolInside80)