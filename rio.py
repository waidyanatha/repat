# REPAT - IO (Input Output) 
#
# Instructions: 
#     - edit values for the settings in config.py
#     - import (include) this library in main
#
# Reporting Patterns (RePat) for determining telecom availability during crises
# ------------------------------------------------------------------------------
#
# purpose of this code is to import and from varoius data sources and then
# output them as a file or stream in the desired formats
#
# contributors: nuwan@lirneasia.net and ilihdian@gmail.com
#
# ------------------------------------------------------------------
#
# import libraries
import sys, os, csv
import pyquery
import pandas as pd
import got
import Exporter as ex
import config as conf
#
# Define a function to remove all symbol characters and replace with a space 
def remove_symbol(str):
    for char in string.punctuation:
        str=str.replace(char,' ')
    return str

# Define a function to remove all symbol characters without replacement
def remove_symbol_nospace(str):
    for char in string.punctuation:
        str=str.replace(char,'')
    return str
#
# cleanup the tweets for processing
def cleanup_tweets(file="./data/rawtweets.csv"):
    # Import csv as pandas object
    dftweets = pd.read_csv(file,delimiter='\t',encoding="ISO-8859-1")
    # not empty then loop through to structure the data
    cols=['Serial','TweetId','permalink','Username','Text','Date','Retweets','Favorites','Mentions','Hashtags','Geo']
    dftmp = pd.DataFrame(columns=cols)

    # Print column headers
    return dftmp

# main function to call to treieve cleaned up tweets for processing
# the data will be stored in the CSV specified in the config.py file
def get_old_tweets(since, until, search, maxtweets):

    #download tweets from every user in the same timeframe
    exstr = 'python2 Exporter.py'
    if since != "" : exstr += ' --since ' + str(since)
    if until != "" : exstr += ' --until ' + str(until)
    if search != "" : exstr += ' --querysearch ' + str(search)
    if maxtweets > -1 : exstr += ' --maxtweets ' + str(maxtweets)
    
#    os.system(exstr)
#fix    data_df=pd.read_csv('tmp.csv',encoding='utf-16',sep='\t')
#    data_df=pd.read_csv('./nepal.txt',encoding='utf-16',sep='\t')
    data_df=pd.read_csv('./data/test200.txt',encoding='utf-16',sep='\t')
    
    return data_df
