import pandas as pd
import numpy as np
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from zipfile import ZipFile

try:
	from urllib import urlopen
except ImportError:
	from urllib.request import urlopen

# import pandas.io.data as web
from datetime import datetime, timedelta
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns

import sys

import requests
from io import BytesIO
import zipfile

import math

import ystockquote
import collections 


def ffRegress(full_df, startDateInt, endDateInt):  #Dates in int form as YYYYMMDD


	#Date Selection
	full_df = full_df[ (endDateInt > full_df['Date']) & (full_df['Date'] > startDateInt)]

	#Regress excess portfolio return on the 5 Fama-French factors ('Mkt-RF', 'SMB', 'HML','RMW', 'CMA', 'RF')
	y = full_df['Excess_Rtrn']
	X = full_df.ix[:,[2,3,4, 5, 6]]
	X = sm.add_constant(X)

	print(full_df.ix[:,[2,3,4, 5, 6]].head())

	model = sm.OLS(y, X)
	results = model.fit() #Alpha is the intercept (aka. const)

	return results 

	
def plotBetas(results):
	#Plotting
	fig = plt.figure(figsize=(12,8))
	fig = sm.graphics.plot_partregress_grid(results, fig = fig)
	plt.show()

def get_price_history(ticker, start_date, end_date):
    """
    example usage:
    get_price_history('appl','2014-11-01','2014-11-30')
    returns a pandas dataframe

    """
    data = ystockquote.get_historical_prices(ticker, start_date, end_date)
    df = pd.DataFrame(collections.OrderedDict(sorted(data.items()))).T
    df = df.convert_objects(convert_numeric=True)
    return df

def constructSP500(full_df):


	numRows = len(full_df.index)

	startDate = int(full_df.loc[full_df.index[0], 'Date'])

	endDate = int(full_df.loc[full_df.index[numRows - 1], 'Date'])


	start_date_FF_format = str(startDate)
	datetimeobject = datetime.strptime(start_date_FF_format,'%Y%m%d')
	start_date_ystockquote_format = datetimeobject.strftime('%Y-%m-%d')

	end_date_FF_format = str(endDate)
	datetimeobject = datetime.strptime(end_date_FF_format,'%Y%m%d')
	end_date_ystockquote_format = datetimeobject.strftime('%Y-%m-%d')


	sp500_df = get_price_history('^GSPC', start_date_ystockquote_format, end_date_ystockquote_format)

	full_df.loc[full_df.index[0], '^GSPC'] = 0




	for dateIndex in range(0, numRows):

		thisDateAsInt = full_df.loc[full_df.index[dateIndex], 'Date']


		date_FF_format = str(int(thisDateAsInt))
		datetimeobject = datetime.strptime(date_FF_format,'%Y%m%d')
		date_ystockquote_format = datetimeobject.strftime('%Y-%m-%d')

		# sp500OnThisDate = sp500_df[date_ystockquote_format]


		sp500OnThisDate = sp500_df.loc[date_ystockquote_format, 'Adj Close']

		full_df.loc[full_df.index[dateIndex], '^GSPC'] = sp500OnThisDate

	return full_df



def constructRiskAdjustedReturnSeries(full_df, increment = 30 ): # <increment> is how many days (defaut = 30 days) to regress at a time

	numRows = len(full_df.index)


	portfolioBalance = full_df['NAV'].iloc[0]


	full_df.loc[full_df.index[0], 'Risk_Adj_NAV'] = portfolioBalance

	alphaList = []

	endHere = False

	for startDateIndex in range(0, numRows, increment):

		if endHere:
			break

		if numRows - startDateIndex < 60:
			endHere = True
			increment = numRows - startDateIndex + 1


		startDateAsInt = full_df.loc[full_df.index[startDateIndex], 'Date'] 

		if (startDateIndex + increment) > numRows:
			endDateAsInt = full_df.loc[full_df.index[numRows - 1], 'Date'] 

		else:
			endDateAsInt = full_df.loc[full_df.index[startDateIndex + increment], 'Date'] 


		print('START: ' + str(startDateAsInt))
		print('END: ' + str(endDateAsInt))

		resultsForThisDateRange = ffRegress(full_df, startDateAsInt, endDateAsInt)

		parameterResultsAsDict = dict(resultsForThisDateRange.params)

		alphaForThisDateRange = parameterResultsAsDict['const']/100
		alphaOnDailyCompoundedBasis = alphaForThisDateRange

		alphaList.append(alphaOnDailyCompoundedBasis)

		# alphaOnDailyCompoundedBasis = math.pow((1 + float(alphaForThisDateRange)),  (1 / increment) ) - 1

		# print(alphaForThisDateRange)
		print('ALPHPA: ' + str(alphaOnDailyCompoundedBasis))

		for dayIndex in range(startDateIndex , min(startDateIndex + increment, numRows - 1)):


			if(dayIndex - 1) < 0:
				continue



			startSP500 = full_df.loc[full_df.index[dayIndex - 1], '^GSPC']

			endSP500 = full_df.loc[full_df.index[dayIndex], '^GSPC']

			sp500ReturnOnThisDate = (endSP500 - startSP500) / startSP500



			benchmarkedRiskAdjustedReturn = alphaOnDailyCompoundedBasis + sp500ReturnOnThisDate


			print(benchmarkedRiskAdjustedReturn)

			full_df.loc[full_df.index[dayIndex], 'Risk_Adj_NAV'] = full_df.loc[full_df.index[dayIndex - 1], 'Risk_Adj_NAV'] * (1 + benchmarkedRiskAdjustedReturn)

			print('RA NAV: ' + str(full_df.loc[full_df.index[dayIndex], 'Risk_Adj_NAV']))


	return full_df, alphaList


def constructRiskAdjustedReturnSeries_InvestedCapital(full_df, increment = 30 ): # <increment> is how many days (defaut = 30 days) to regress at a time



	numRows = len(full_df.index)


	#Correct outliers (drastic changes in NAV here correspond to major paring up or down in the amount of invested capital, not in our actual performance on that day
					#  So let's just set those values equal to 0)



	mask = np.abs(full_df['Excess_Rtrn']) > full_df['Excess_Rtrn'].mean() + 3 * full_df['Excess_Rtrn'].std()
	full_df.loc[mask, 'Excess_Rtrn'] =  0

	print(full_df['Excess_Rtrn'].max())
	print(full_df['Excess_Rtrn'].min())

	# sys.exit(0)

	#Rest of method is same

	return constructRiskAdjustedReturnSeries(full_df, increment = 30 )



# def constructRiskAdjustedReturnSeries_InvestedCapital(full_df, trade_dates ): # <increment> is how many days (defaut = 30 days) to regress at a time

# 	numRows = len(full_df.index)


# 	portfolioBalance = full_df['NAV'].iloc[0]


# 	full_df.loc[full_df.index[0], 'Risk_Adj_NAV'] = portfolioBalance

# 	firstPortfolioDate = full_df.loc[full_df.index[0], 'Date']

# 	lastPortfolioDate = full_df.loc[full_df.index[ numRows - 1], 'Date']


# 	trade_dates = [date for date in trade_dates if lastPortfolioDate > date > firstPortfolioDate]

# 	trade_dates.append(firstPortfolioDate)

# 	trade_dates.sort()



# 	for trade_dates_index in range(len(trade_dates)):



# 		startDateAsInt = trade_dates[trade_dates_index]
# 		startDateIndex = list(full_df['Date']).index(startDateAsInt)


# 		# startDateAsInt = full_df.loc[full_df.index[startDateIndex], 'Date'] 

# 		if trade_dates_index >= len(trade_dates) - 1:
# 			endDateAsInt = full_df.loc[full_df.index[numRows - 1], 'Date'] 
# 			endDateIndex = numRows - 1

# 		else:
# 			endDateAsInt = trade_dates[trade_dates_index + 1]
# 			endDateIndex = list(full_df['Date']).index(endDateAsInt)


# 		increment = endDateIndex - startDateIndex

# 		print('START: ' + str(startDateAsInt))
# 		print('END: ' + str(endDateAsInt))

# 		if increment < 2:
# 			parameterResultsAsDict = {'const' : 0}


# 		else:

# 			resultsForThisDateRange = ffRegress(full_df, startDateAsInt, endDateAsInt)

# 			parameterResultsAsDict = dict(resultsForThisDateRange.params)

# 		alphaForThisDateRange = parameterResultsAsDict['const']/100

# 		alphaOnDailyCompoundedBasis = math.pow((1 + float(alphaForThisDateRange)),  (1 / increment) ) - 1

# 		print(alphaForThisDateRange)
# 		print(alphaOnDailyCompoundedBasis)

# 		for dayIndex in range(startDateIndex , endDateIndex):


# 			if(dayIndex - 1) < 0:
# 				continue



# 			startSP500 = full_df.loc[full_df.index[dayIndex - 1], '^GSPC']

# 			endSP500 = full_df.loc[full_df.index[dayIndex], '^GSPC']

# 			sp500ReturnOnThisDate = (endSP500 - startSP500) / startSP500



# 			benchmarkedRiskAdjustedReturn = alphaOnDailyCompoundedBasis + sp500ReturnOnThisDate


# 			print(benchmarkedRiskAdjustedReturn)

# 			full_df.loc[full_df.index[dayIndex], 'Risk_Adj_NAV'] = full_df.loc[full_df.index[dayIndex - 1], 'Risk_Adj_NAV'] * (1 + benchmarkedRiskAdjustedReturn)


# 	return full_df

def main():

	#Download Fama-French 5-factor data
	url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
	request = requests.get(url)
	file = zipfile.ZipFile(BytesIO(request.content))


	FFdata = pd.read_csv(file.open('F-F_Research_Data_5_Factors_2x3_daily.CSV'), 
	                     header = 0, names = ['Date','Mkt-RF', 'SMB', 'HML','RMW', 'CMA', 'RF'],
	                     skiprows=3)





	#Convert into float
	FFdata = FFdata.astype('float')
	FFdata.tail()




	tradeHistory_df = pd.read_csv('TradeHistory.csv', header = 0)

	allTradeDates = list(set(list(tradeHistory_df['date'])))
	allTradeDates.sort()

	allTradeDates = [int(datetime.strptime(date,'%m/%d/%y').strftime('%Y%m%d')) for date in allTradeDates]


	print(allTradeDates)

	
	# Read in portfolio data
	nav_df = pd.read_csv('Portfolio Data_031317.csv', header = 0)#, names = column_names)

	nav_df_invested_cap = pd.read_csv('Invested Capital_031317.csv', header = 0)#, names = column_names)

	navList = [nav_df, nav_df_invested_cap]

	navNamesList = ['total_cap', 'invested_cap']

	for navIndex in range(len(navList)):

		nav_df = navList[navIndex]

		navName = navNamesList[navIndex]

		#Merge dataframes

		full_df = pd.merge(nav_df, FFdata, left_on='Date', right_on='Date', how='outer')
		full_df = full_df.dropna()

		#Calcualte portfolio daily returns
		full_df['NAV_Change'] = full_df['NAV'].pct_change()*100

		#Calculate excess portfolio return over the risk free rate
		full_df['Excess_Rtrn'] = (full_df['NAV_Change']- full_df['RF'])

		full_df = full_df.dropna()

		full_df = constructSP500(full_df)


		mask = np.abs(full_df['Excess_Rtrn']) > full_df['Excess_Rtrn'].mean() + 3 * full_df['Excess_Rtrn'].std()
		full_df.loc[mask, 'Excess_Rtrn'] =  0


		currentDate = 20170327
		ttmDate = 20160327
		ytdDate = 20170101


		



		# plotBetas(results)

		full_df_ttm = full_df[ full_df['Date'] > ttmDate]
		full_df_ytd = full_df[ full_df['Date'] > ytdDate]


		nameList = ['TTM', 'YTD']

		dfList = [full_df_ttm, full_df_ytd]

		dateList = [ttmDate, ytdDate]


		for index in range(len(dfList)):

			full_df = dfList[index]

			dateName = nameList[index]

			results = ffRegress(full_df, dateList[index], currentDate)

			print(results.summary()) #Alpha is the intercept (aka. const)

			# sys.exit(0)

			parameterResultsAsDict = dict(results.params)

			
			if navName.find('invested_cap') == -1:
				full_df, alphaList = constructRiskAdjustedReturnSeries(full_df, increment =  30)

			else:
				full_df, alphaList = constructRiskAdjustedReturnSeries_InvestedCapital(full_df, increment = 30 )




			print(full_df['Excess_Rtrn'].max())
			print(full_df['Excess_Rtrn'].min())




			print(full_df)


			full_df = full_df.dropna()

			full_df['Risk_Adj_NAV'] = full_df['Risk_Adj_NAV']/full_df.loc[full_df.index[0], 'Risk_Adj_NAV'] - 1
			print(full_df['Risk_Adj_NAV'])

			full_df['^GSPC'] = full_df['^GSPC']/full_df.loc[full_df.index[0], '^GSPC'] - 1

			full_df['NAV'] = full_df['NAV']/full_df.loc[full_df.index[0], 'NAV'] - 1



			full_df[['Date', 'Risk_Adj_NAV', '^GSPC', 'NAV']] .to_csv('risk_adj_returns_%s.csv' % (navName + '_' + dateName) , sep = ',')

			# full_df[['Risk_Adj_NAV', '^GSPC', 'NAV', 'Date']].plot(x = 'Date')
			# plt.show()



			print('NUM MONTHS WITH POSITIVE ALPHA: ' + str( sum(np.array(alphaList) > 0 ) ))
			print('NUM MONTHS TOTAL: ' + str( len(alphaList) ))
			print('AVG MONTHLY ALPHA: ' + str( np.mean(alphaList) ))






main()

	



