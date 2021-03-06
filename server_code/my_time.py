""" This module handles all sorts of time handling operations

Author: Noor
Date: March 13, 2021

TODO: Add support for leap year

Idea: Enumerate each year (inclusive) between year1 and year2
Determine how many of these are leap years
Perform an increment in days for EACH leap year
"""
# Import the standard time library
import time

from pyfiglet import Figlet

# this is to help month/days conversions
days_in_months = {
	1: 31,
	2: 28,
	3: 31,
	4: 30,
	5: 31,
	6: 30,
	7: 31,
	8: 31,
	9: 30,
	10: 31,
	11: 30,
	12: 31
}

def convert_str_secs(time_str):
	"""Converts a str format time into seconds since epoch"""
	return time.mktime(time.strptime(time_str))

def show_time_to(time_str):
	"""Takes a time_str as input and provides a comma separated
	string to show how far we are 'from' that time in the future"""

	# Convert the given string to time struct
	time2 = time.strptime(time_str)

	# Get current time from the system
	time1 = time.localtime()
	relative_str = ""

	# creating local variable to improve readability
	month1 = time1[1]
	day1 = time1[2]
	hour1 = time1[3]
	min1 = time1[4]
	sec1 = time1[5]

	day2 = time2[2]
	hour2 = time2[3]
	min2 = time2[4]
	sec2 = time2[5]

	if sec2 < sec1:
		# seconds remaining in current min + sec in target minute
		secs = (60-sec1) + sec2
		# 1 minute subtracted from target minute
		min2 -= 1
	else:
		secs = sec2 - sec1
	relative_str = ":{}s".format(secs) + relative_str

	if min2 < min1:
		# minutes remaining in current hr + mins pas in target hr
		mins = (60-min1) + min2
		hour2 -= 1
	else:
		mins = min2 - min1
	relative_str = ":{}m".format(mins) + relative_str

	if hour2 < hour1:
		# hours remaining in the current day + hrs in target day
		hours = (24-hour1) + hour2
		day2 -= 1
	else:
		hours = hour2 - hour1
	relative_str = ":{}h".format(hours) + relative_str

	if day2 < day1:
		# days left in cur month + days in target month
		days = (days_in_months[month1] - day1) + day2
	else:
		days = day2 - day1

	relative_str = "{}d".format(days) + relative_str

	return relative_str

def show_time_since(time_str):
	"""Takes a time value as input, in form of asctime() string
	and provides a string representation of relative time since,
	that time"""
	# Convert the given string to time struct
	time1 = time.strptime(time_str)

	# Get current time from the system
	time2 = time.localtime()
	relative_str = ""

	# creating local variable to improve readability
	year1 = time1[0]
	month1 = time1[1]
	day1 = time1[2]
	hour1 = time1[3]
	min1 = time1[4]
	sec1 = time1[5]

	year2 = time2[0]
	month2 = time2[1]
	day2 = time2[2]
	hour2 = time2[3]
	min2 = time2[4]
	sec2 = time2[5]

	# if year changed, show only year and month
	if year2 > year1:
		years = year2 - year1
		if month2 >= month1:
			months = month2 - month1
		else:
			# months left in prev year + months in this year
			months = (12 - month1) + month2
			years -= 1
		if years == 1:
			relative_str += "{} year ".format(years)
		else:
			relative_str += "{} years ".format(years)

		if months == 1:
			relative_str += "{} month ".format(months)
		else:
			relative_str += "{} months ".format(months)

	# If the month in the dates has changed, show only month and days
	elif month2 > month1:
		months = month2 - month1
		if day2 >= day1:
			days = day2 - day1
		else:
			# TODO: adjust this for leap years
			# days left in previous month + days passed in current month
			days = (days_in_months[month2-1]-day1) + day2
			months -= 1
		
		if months == 1:
			relative_str += "{} month ".format(months)
		else:
			relative_str += "{} months ".format(months)
		
		if days == 1:
			relative_str += "{} day ".format(days)
		else:
			relative_str += "{} days ".format(days)

	# if day changed, show days and hours
	elif day2 > day1:
		days = day2 - day1
		if hour2 >= hour1:
			hours = hour2 - hour1
		else:
			# hours left from prev day + hours passed in current day
			hours = (24 - hour1) + hour2
			days -= 1

		if days == 1:
			relative_str += "{} day ".format(days)
		else:
			relative_str += "{} days ".format(days)
		
		if hours == 1:
			relative_str += "{} hour ".format(hours)
		else:
			relative_str += "{} hours ".format(hours)
		

	# if hour changed, show hours and minutes
	elif hour2 > hour1:
		hours = hour2 - hour1    

		if min2 >= min1:
			mins = min2 - min1
		else:
			# mins left in the prev hr + mins past in current hr
			mins = (60 - min1) + min2
			hours -= 1

		if hours == 1:
			relative_str += "{} hour ".format(hours)
		else:
			relative_str += "{} hours ".format(hours)

		if mins == 1:
			relative_str += "{} min ".format(mins)
		else:
			relative_str += "{} mins ".format(mins)

	# if minute changed, show minutes and seconds
	elif min2 > min1:
		mins = min2 - min1

		if sec2 > sec1:
			secs = sec2 - sec1
		else:
			# secs left in the prev in + secs past in current min
			secs = (60 - sec1) + sec2
			mins -= 1

		if mins == 1:
			relative_str += "{} min ".format(mins)
		else:
			relative_str += "{} mins ".format(mins)

		if secs == 1:
			relative_str += "{} sec ".format(secs)
		else:
			relative_str += "{} secs ".format(secs)

	# else, show "less than a minute"
	elif min2 <= min1:
		relative_str += "less than a minute "

	# add "ago" to the str
	relative_str += "ago"

	return relative_str

# event_end_str = "Sat Mar 13 13:15:00 2021"
# msg_figlet = Figlet()
# status_msg = "\n{}\n".format(msg_figlet.renderText(show_time_to(event_end_str)))
# print(status_msg)