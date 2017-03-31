'''
This code takes a ticker, pulls down all 10-Ks available from the SEC Edgar database, and writes the contents of those 10-Ks to textfiles
'''

from pprint import pprint
import requests
from bs4 import BeautifulSoup
import sys
import html2text
import os



chars = {
	'\xc2\x82' : ',',        # High code comma
	'\xc2\x84' : ',,',       # High code double comma
	'\xc2\x85' : '...',      # Tripple dot
	'\xc2\x88' : '^',        # High carat
	'\xc2\x91' : '\x27',     # Forward single quote
	'\xc2\x92' : '\x27',     # Reverse single quote
	'\xc2\x93' : '\x22',     # Forward double quote
	'\xc2\x94' : '\x22',     # Reverse double quote
	'\xc2\x95' : ' ',
	'\xc2\x96' : '-',        # High hyphen
	'\xc2\x97' : '--',       # Double hyphen
	'\xc2\x99' : ' ',
	'\xc2\xa0' : ' ',
	'\xc2\xa6' : '|',        # Split vertical bar
	'\xc2\xab' : '<<',       # Double less than
	'\xc2\xbb' : '>>',       # Double greater than
	'\xc2\xbc' : '1/4',      # one quarter
	'\xc2\xbd' : '1/2',      # one half
	'\xc2\xbe' : '3/4',      # three quarters
	'\xca\xbf' : '\x27',     # c-single quote
	'\xcc\xa8' : '',         # modifier - under curve
	'\xcc\xb1' : '' ,         # modifier - under line
	'\x97': ' '
}
def replace_chars(s):
	for badChar in chars:
		s.replace(badChar, chars[badChar])
	return s

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


def download10K(ticker):
	
	print(ticker)

	outFileName = 'all10Ks/' + ticker + '/' 

	if  os.path.exists(os.path.dirname(outFileName)):
		return

	cikCodeForTicker = tickerToCIKDict[ticker]
	
	baseURL = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=10-K&dateb=&owner=exclude&count=100'
	
	
	pageOfReportLinks = baseURL % cikCodeForTicker
	
	# print(pageOfReportLinks)
	#Get all 10-K page links (not 10-K report links)
	
	
	
	
	page = requests.get(pageOfReportLinks)
	soup = BeautifulSoup(page.text, 'lxml')

 
	
	
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
	
	#allYears = ['2015']
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

	dictOfFilingDates = {}
	for year in allYears:
		thisURL = dictOf10KSummaryURLs[year]
	
		summaryPage = requests.get(thisURL)
		soup = BeautifulSoup(summaryPage.text, "html.parser")
		
		filing_date = soup.findAll("div", {"class": "formGrouping"})[0].find("div", {"class" : "info"}).get_text()

		dictOfFilingDates[year] = filing_date
	
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
	
	# pprint(dictOf10KHtmURLs)
	#Get the text for all 10Ks
	
	dictOf10KTexts = {}
	
	for year in allYears:
		# print(year)

		filing_date = dictOfFilingDates[year]

		outFileName = 'all10Ks/' + ticker + '/' + ticker + '_10K_' + year + '_' + filing_date + '.txt'

		if not os.path.exists(os.path.dirname(outFileName)):
			try:
				os.makedirs(os.path.dirname(outFileName))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
					raise


		outfile = open(outFileName, "w") 
	
		thisYear10KURL = dictOf10KHtmURLs[year]
		# print(thisYear10KURL)
		# textForThisYear10K = BeautifulSoup(requests.get(thisYear10KURL).text).get_text()

		textForThisYear10K =  html2text.html2text(requests.get(thisYear10KURL).text)
		# textForThisYear10K = html2text.html2text(html)
		textForThisYear10K = textForThisYear10K.replace(u'\xa0', u' ')



		# pprint(textForThisYear10K)
		dictOf10KTexts[year] = textForThisYear10K
		outfile.write(textForThisYear10K.encode("ascii", "replace").decode("utf-8"))
		outfile.close()
		# sys.exit(0)



tickers = list(tickerToCIKDict.keys())
tickers = sorted(tickers)

# tickers = ['CAS']#['AAPL', 'GOOG', 'SAVE']
count = 0
for ticker in tickers:
	print(count)
	count = count + 1
	try:
		download10K(ticker)
	except:
		continue
	
