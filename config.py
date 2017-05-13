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
# set the ISO 3166-1 ALPHA-2 country code to the data set filter by country 
ISO_3166_1_APLPHA_2 = "np"     #Nepal
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
#maximum = -1                # maximum = -1 implies all records
maximum = 100             # will retrieve the top 100 records
#
##################################################################################
#
# FILES for storing processed data at various stages
#
# @instructions:
#     you may change the files names but the file extensions must be preserved
#     all data files will be stored in the directory folder: ./data/
#
# @purpose:
#     to be able to start a process at any point in the main.py without to repeat
#     the previous lengthy process by such as data clustering, extraction, etc 
#     User may simply comment the function in main.py MAIN CALLS to skip the step
##################################################################################
#
file_raw_extract_data = "tmp_alltweets.csv"
#file_raw_data_extract = "tmp_allquakemap.csv"
#
# other temporary files of the data set at various stages of the processing
#
file_formatted_data = "test200.txt"
#file_clean_data_from_extract = "tmp_clean_quakemap.txt"
file_clustered_data = "tmp_clustered_tweets.csv"
#file_clustered_data = "tmp_clustered_quakemap.csv"
file_no_noise_data = "tmp_no_noise_tweets.csv"
#file_no_noise_data = "tmp_no_noise_quakemap.csv"
file_density_data = "tmp_density_tweets.csv"
#file_density_data = "tmp_density_quakemap.csv"
file_plotting_data = "tmp_plotting_tweets.csv"
#file_plotting_data = "tmp_plotting_quakemap.csv"
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