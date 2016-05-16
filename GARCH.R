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

differ = diff(prices)

spec = ugarchspec(mean.model = list(armaOrder=c(0,0)), variance.model = list( garchOrder = c(1, 1))) 
#ugarchspec(variance.model = list(model = 'eGARCH', garchOrder = c(2, 1)), distribution = 'std')



fit = ugarchfit(spec, differ )
plot(fit) # 1 gives series of log-returns with a plot of conditional SD (#3) on top and -Conditional SD on bottom
# Residuals look normally distributed



# These are forecasts
forc1 = ugarchforecast(fit, n.ahead= 30)

U = uncvariance(fit)^0.5 # Unconditional standard deviation


forcSigmas=as.matrix(sigma(forc1))
forcSeries=as.matrix(fitted(forc1))



plot(as.matrix(fitted(fit)),type='l') # Don't know why these values are so small
lines(differ,col='green')

forecastResult = forecast(auto.arima(prices,d=1),h=15)
forecastResult$fitted


logreturns = diff(log(prices))
mu = mean(exp(logreturns)-1)


fitt = c(sqrt(as.matrix(sigma(fit))^2*mu^2), rep("",30))
pred = c(rep("",length(fitt)-30), sqrt(forcSigmas^2*mu^2))
plot(fitt,type='l',main='S&P500 Daily Volatility (Conditional SD) Forecasted 30 Days Using GARCH', ylab='Volatility (Conditional SD)', xlab='Time (From 2014-03-25 To 2016-03-25, Forecasted 30  Days Thereafter)')
lines(pred, col='red')
total = c(sqrt(as.matrix(sigma(fit))^2*mu^2),sqrt(forcSigmas^2*mu^2))
plot(total,type='l',main='S&P500 Daily Volatility (Conditional SD) Forecasted 30 Days Using GARCH', ylab='Volatility (Conditional SD)', xlab='Time (From 2014-03-25 To 2016-03-25, Forecasted 30  Days Thereafter)')








# This next block of code does the same as plot(fit) from the rugarch package, but instead we use the fGarch package
fit1 = garchFit(~ garch(1, 1), data = logreturns, trace = FALSE)
predict(fit1,n.ahead=20,conf=.99,plot=TRUE)

spec = garchSpec(model = list(mu = 0.000628, ar = 0, omega = 0.000005, alpha = 0.180787, gamma = 0, beta = 0.766278))
y = garchSim(spec = spec, n = 500)
x=garchFit(formula =~arma(0, 0) + aparch(1,1), data=y, cond.dist="norm", trace=FALSE, include.delta=FALSE)
x@fit$coef
#conditional mean forecast
as.numeric(predict(x,1)[1])
x@fit$coef[1]+x@fit$coef[2]*y[length(y)]
#conditional std forecast
as.numeric(predict(x,1)[3])
sqrt(x@fit$coef[3]+x@fit$coef[4]*((x@fit$series$z[length(x@fit$series$z)])^2)+x@fit$coef[6]*x@fit$series$h[length(x@fit$series$h)]+x@fit$coef[5]*((x@fit$series$z[length(x@fit$series$z)])^2)*(x@fit$series$z[length(x@fit$series$z)]<0))
plot(x)
