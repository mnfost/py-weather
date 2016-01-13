#!/usr/bin/env python
### historical weather data collector ###
######### October 7, 2015 ########
########## Mindy Foster ##########
## http://www.wunderground.com/history/ ##
##
##
## location -- list of locations in city,state format
## date -- list of dates to gather weather
##
## All lists must be the same length!!
## Program will get weather data in order of lists
## Example: location[0], date[0], location[1], date[1], location[2], date[2], etc.
##




from BeautifulSoup import BeautifulSoup
import sys, os, datetime, MySQLdb, re, itertools
from logging import getLogger, Handler
from urllib import urlopen
from warnings import simplefilter
from time import sleep
from re import search
from MySQLdb import DateFromTicks


class NullHandler(Handler):
	def emit(self, record):
		pass

class CONSTANTS:
	BASE = 'http://www.wunderground.com/history/airport'
	FETCH_TRIES = 10

class Fetcher:
	@classmethod
	def fetch(self, url):
		for i in xrange(CONSTANTS.FETCH_TRIES):
			logger.debug('FETCH %s' % url)
			try:
				page = urlopen(url)
			except IOError, e:
				if i == CONSTANTS.FETCH_TRIES-1:
					logger.error('ERROR %s (max tries %s exhausted)' % (url, CONSTANTS.FETCH_TRIES))
				sleep(1)
				continue
			if page.getcode() == 404:
				return ""
			else:
				return page.read()
			break

logger = getLogger('weather')
logger.addHandler(NullHandler())

class Store:
	def __init__(self, **args):
		user = raw_input("Please enter your MySQL username: ")
		pw = raw_input("Please enter your MySQL password: ")
		db = raw_input("Please enter the name of the MySQL database: ")
		
		args = {'user': user, 'passwd': pw, 'db': db, 'charset': 'utf8'}
		self.db = MySQLdb.connect(**args)
		self.cursor = self.db.cursor()
	
	def save(self):
		self.db.commit()
	
	def finish(self):
		self.db.commit()
		self.db.close()
	
	def query(self, query, values = None):
		simplefilter("error", MySQLdb.Warning)
		try:
			res = self.cursor.execute(query, values)
			return self.cursor.fetchall()
		except (MySQLdb.Error, MySQLdb.Warning), e:
			if type(e.args) is tuple and len(e.args) > 1:
				msg = e.args[1]
			else:
				msg = str(e)
			logger.error('%s\nQUERY: %s\nVALUES: %s\n\n' % (msg, query, ','.join([unicode(v) for v in values])))

## Validate Date
def validate(date):
	try:
		datetime.datetime.strptime(date, '%Y/%m/%d')
	except:
		sys.exit("Incorrect date format, should be %Y/%m/%d")

## Get Airport Code
def get_airport(location):
	l = location.split(',')
	if len(l) != 2:
		sys.exit("Incorrect location format, should be city,state")
	url = 'http://www.travelmath.com/nearest-airport/%s,+%s' % (l[0],l[1])
	contents = Fetcher.fetch(url)
	soup = BeautifulSoup(contents)
	t = soup.findAll('a')
	for r in t:
		if len(re.findall('http://www.travelmath.com/airport/', str(r))) != 0:
			r = re.sub('<a href="http://www.travelmath.com/airport/','', str(r))
			airport = r[0:3]
			break
	return airport


## Get Weather Data
def weather(location, date):
	FIELDS = ['location', 'date', 'local_time', 'temp', 'dew_point', 'humidity', 'pressure', 'visibility', 'wind_dir', 'wind_speed', 'gust_speed', 'precip', 'events', 'conditions']
	FIELDS1 = ['location', 'date', 'local_time', 'temp', 'heat_index','dew_point', 'humidity', 'pressure', 'visibility', 'wind_dir', 'wind_speed', 'gust_speed', 'precip', 'events', 'conditions']
	##
	airport = get_airport(location)
	##
	url = '%s/%s/%s/DailyHistory.html?reqdb.magic=1&reqdb.wmo=99999' % (CONSTANTS.BASE, airport, date)
	contents = Fetcher.fetch(url)
	if contents is None:
		return
	soup = BeautifulSoup(contents)
	hist = []
	for row in soup.findAll('tr'):
		if len(row.findAll('td')) == 12:
			n = 3
			values = {}
			values['location'] = location
			values['date']= date
			values['heat_index']=''
			for col in row.findAll('td'):
				a = re.sub('(<.*?>|&.*?;)','',str(col)).strip('\n')
				values[FIELDS[n]] = a
				n+=1
				if n == 14:
					hist.append(values)
		if len(row.findAll('td')) == 13:
			n = 3
			values = {}
			values['location'] = location
			values['date']= date
			for col in row.findAll('td'):
				a = re.sub('(<.*?>|&.*?;)','',str(col)).strip('\n')
				values[FIELDS1[n]] = a
				n+=1
				if n == 15:
					hist.append(values)
	return hist

## Main Code
def get_weather(location, date):
	os.system('mysql.server restart')
	DB = Store()
	validate(date[0])
	if len(location) != len(date):
		sys.exit("All variables must have the same length!")
	for r in range(len(location)):
		ab = weather(location[r], date[r])
		for h in ab:
			keys = [k for k in h.keys()]
			values = [None if h[k] == '' else h[k] for k in keys]
			sql ='REPLACE INTO weather (%s) VALUES(%s)' % (','.join(keys), ','.join(['%s'] * len(keys)))
			DB.query(sql, values)
			DB.save()
	DB.finish()

