
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



#Stress testing

numberOfVariables = length(names(var$varresult$SAVEL$coefficients))


#We want all changes to be 0, except for the one variable we are testing
newdata = matrix(0, nrow = 1, ncol = numberOfVariables)

indexOfVariableYouWantToManipulate = 3 #Oil


#Last two variables are constant and trend, so these must be 1
newdata[,numberOfVariables] = 1
newdata[,numberOfVariables -1] = 1

#Manipulate the one variable
variableChange = -.1
logReturnForChangedVariable = log(1 +variableChange )
newdata[indexOfVariableYouWantToManipulate] = logReturnForChangedVariable


newdata  = data.frame(newdata)


colnames(newdata) <- names(var$varresult$SAVEL$coefficients)

predictionInterval = predict(var$varresult$SAVEL, newdata, interval = "predict")
