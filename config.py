# REPAT - CONFIGURATION
#
# Instructions - Configure the file to enable/disable parameters
#                and determine which functions to execute to 
#                achieve your desired results
#
# contributors: nuwan@lirneasia.net
#
# ------------------------------------------------------------------
#
# import libraries
import sys, os
#
##################################################################################
#
# Parameters for DATA IMPORT
#
##################################################################################
# uncomment the source to retrieve data from; only one at a time and not all
# we have scripts in rio.py to import data for each of the sources
source = "twitter"       # available
#source = "ushahidi"     # work-in-progress
#source = "facebook"     # unavailable 
#
# indicate the file name you wish to store all the data retrieved from the source
# the file will be stored in CSV fomat in the folder ./data
outfile = "alltweets.csv"
#
# set the ISO two letter country code to the data set filter by country 
country = "np"     #Nepal
#country = "it"     # Italy
#
# set the start and end (yyyy-mm-dd) to filter the data set by dates
# when retrieving from the source
# todo: remove this option and allow user to specify the data of the event
#       and the length of the period (e.g. 20 days) to retrieve data for
#       20 days before and after the event date
startdate = "2015-04-11"
enddate = "2015-05-19"
#
# set the query string to filter the data from the source
search = "nepal"
#
# set the event specific data
event = "nepal earthquake"
event_datetime = "4/25/2015 12:00:00"     # m/d/yyyy hh:mm:ss date and time the event was recorded
location = "Gurkha"         # epicenter of the event
lattitude = ""              # lat coordinate of the epicenter in decimal form
longitude = ""              # lon coordinate of the epicenter in decimal form
# todo: currently we are using the radius but in the future we should offer a polygon too
radius = 400                # radius, in km, of the geographic are to filter source data
#
# set the maximum number of records to retrieve
maximum = -1                # maximum = -1 implies all records
#maximum = 10000             # will retrieve the top 10,000 records
#
##################################################################################
#
# Parameters for DATA CLUSTERING
#
##################################################################################
#
# The two parameters are used to calculate the bounds of the N-Sphere defined by
# the orthogonal attributes Longitude, Latitude, and Time
#
# Diameter of the N-Sphere distance parameters in KM
maximum_displacement = 5
# Diameter of the N-Sphere time parameter in HOURS
maximum_period = 12