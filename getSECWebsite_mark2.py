'''
This code takes a ticker, pulls down all 10-Ks available from the SEC Edgar database, and writes the contents of those 10-Ks to textfiles
'''

from pprint import pprint
import requests
from bs4 import BeautifulSoup
import sys

def loadTickerToCIKCrosswalk():
	infile = open('cik-ticker.csv', 'r')

	crosswalkDict = {}

	for line in infile:
		line = line.strip()
		thisRow = line.split(',')
		ticker = thisRow[0]
		cik = thisRow[1]

		crosswalkDict[ticker] = cik

	return crosswalkDict



tickerToCIKDict = loadTickerToCIKCrosswalk()


#Get page listing links to 10-K pages (not links to 10-K reports)
ticker = 'SAVE'

cikCodeForTicker = tickerToCIKDict[ticker]


baseURL = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=10-K&dateb=&owner=exclude&count=100'


pageOfReportLinks = baseURL % cikCodeForTicker

print(pageOfReportLinks)
#Get all 10-K page links (not 10-K report links)




page = requests.get(pageOfReportLinks)
soup = BeautifulSoup(page.text)


table = soup.find('table', attrs={'class':'tableFile2', 'summary':'Results'})

# pprint(table)
rows = table.find_all('tr')

data = []




'''
https://www.sec.gov/Archives/edgar/data/1090872/000104746910010499/0001047469-10-010499-index.htm
http://www.sec.gov/Archives/edgar/data/320193/000119312510238044/0001193125-10-238044-index.htm
'''

for row in rows:
	cols = row.find_all('td')
	# try:
	# 	print(cols[1].find('a').get('href'))
	# except:
		# print('')
	cols = [ele.text.strip()  if not ele.find('a') else ele.find('a').get('href')  for ele in cols]
	data.append([ele for ele in cols if ele]) # Get rid of empty values




dictOf10KSummaryURLs = {}


for row in range(len(data)): 
	if len(data[row]) <= 0 or  data[row][0] != '10-K': #If this report is not a 10-K, move on, otherwise let's get the link
		continue


	urlExt = data[row][1]
	summaryPageForThis10K = 'http://www.sec.gov' + urlExt

	date = data[row][3]
	year = date[: date.find('-')]



	dictOf10KSummaryURLs[year] = summaryPageForThis10K



allYears = list(dictOf10KSummaryURLs.keys())
allYears.sort()


#Get all values of the access number (a201610-k9242016.htm) for all 10Ks


dictOf10KHtmURLs = {}

'''
This is what the table we are parsing looks like


Seq	Description	Document	Type	Size
1	10-K	a201610-k9242016.htm	10-K	2497746
2	EXHIBIT 10.18	exhibit101810k2016.htm	EX-10.18	53056
3	EXHIBIT 10.19	exhibit101910k2016.htm	EX-10.19	73664
4	EXHIBIT 12.1	exhibit12110k2016.htm	EX-12.1	47668
5	EXHIBIT 21.1	exhibit21110k2016.htm	EX-21.1	5777
6	EXHIBIT 23.1	exhibit23110k2016.htm	EX-23.1	10195
7	EXHIBIT 31.1	exhibit31110k2016.htm	EX-31.1	13323
8	EXHIBIT 31.2	exhibit31210k2016.htm	EX-31.2	13459
9	EXHIBIT 32.1	exhibit32110k2016.htm	EX-32.1	12007
16		a201610-k9_chartx38133.jpg	GRAPHIC	67906
17		g66145g66h99.jpg	GRAPHIC	10963
 	Complete submission text file	0001628280-16-020309.txt	 	13277662

We want: a201610-k9242016.htm

'''
for year in allYears:
	thisURL = dictOf10KSummaryURLs[year]

	summaryPage = requests.get(thisURL)
	soup = BeautifulSoup(summaryPage.text)


	table = soup.find('table', attrs={'class':'tableFile'})

	rows = table.find_all('tr')

	data = []

	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		data.append([ele for ele in cols if ele]) # Get rid of empty values


	#Get cell with 10K access number

	for row in range(len(data)):
		for col in range(len(data[row])):
			thisCell = str(data[row][col])

			if '10-K' in str(thisCell) or 'FOR THE FISCAL YEAR ENDED' in str(thisCell) or 'ANNUAL REPORT' in str(thisCell) :

				correctColumn = col + 1
				accessNumber = str(data[row][correctColumn])

				break


			

	baseURLForThisYear = thisURL[ : thisURL.rfind('/') + 1]

	dictOf10KHtmURLs[year] = baseURLForThisYear + accessNumber

pprint(dictOf10KHtmURLs)
#Get the text for all 10Ks

dictOf10KTexts = {}

for year in allYears:
	print(year)
	outfile = open(ticker + '_10K_' + year + '.txt', 'w')


	thisYear10KURL = dictOf10KHtmURLs[year]
	print(thisYear10KURL)
	textForThisYear10K = BeautifulSoup(requests.get(thisYear10KURL).text).get_text()

	dictOf10KTexts[year] = textForThisYear10K


	outfile.write(textForThisYear10K)

	outfile.close()

