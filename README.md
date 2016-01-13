# py-weather
Given a location and date, the program will collect ('temp', 'dew_point', 'humidity', 'pressure', 'visibility', 'wind_dir', 'wind_speed', 'gust_speed', 'precip', 'events', 'conditions') for all hours of that given date/location.


# Requirements
Python 2.6+ (2.5 will not work)
BeautifulSoup http://www.crummy.com/software/BeautifulSoup/
MySQLDb
MySQL 5.0 and up, maybe 4.x too

# Usage
Create the schema:
mysql -D weather < py-weather.sql

Use:
get_weather(location, airport, date)

Variables:
location -- list of locations in city,state format
date -- list of dates to gather weather

All lists must be the same length!!
Program will get weather data in order of lists (i.e. location[0], date[0], location[1], date[1], location[2], date[2], etc.)

