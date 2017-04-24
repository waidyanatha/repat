# REPAT - MAIN 
#
# Instructions: 
#     - edit values for the settings in config.py
#     - execute this file with Python2 to build the 
#       input data and outputs density clusters
#
# Reporting Patterns (RePat) for determining telecom availability during crises
# ------------------------------------------------------------------------------
#
# purpose of this code-base is to make use of spatial and temporal 
# data obtained from various sources that are generated through 
# people reporting during a crisis to determine the telecom 
# availability based on theanormalies detected in the reporting 
# behaviour (or patterns)
#
# contributors: nuwan@lirneasia.net and ilihdian@gmail.com
#
# ------------------------------------------------------------------------------
#
# import libraries
import sys, os
import numpy as np
import pandas as pd
import config as conf
import rio
import cluster
import plot

# 1. get cleaned and formatted data from a source: twitter, facebook, g+, ushahidi,
# define the function blocks for retieving data filtered by parameters in config.py
def twitter():
    df = rio.get_old_tweets(conf.startdate,conf.enddate,conf.search,conf.maximum)
    print("twitter\n")
    return df

def ushahidi():
    print ("ushahidi\n")

def other():
    print ("other\n")

# 2. density-wise cluster the data by time and distances
# e.g. all data points that are within a 2km redius and a 24 time period
#
# inputs: den_df is a python pandas dataframe
#d def density_wise_cluster(cluster_df):
def get_clusters(cluster_df):
    print("starting to cluster the event data ...")
#        print('{0}\r'.format("trying to cleanup and format all data ...")),
    print("trying to cleanup and format all data ...")
    cluster_df = cluster.clean_data(cluster_df)
    print(str(len(cluster_df.index)-1) + " dataframe records cleaned and formatted !")
    # remove duplicates with identical Serial, Date, Lat, Lon, & Username
    print("removing duplicates rows with same Serial, User, Date, and Coordinates ...")
    cluster_df = cluster_df.drop_duplicates()
    #
    # cluster the data
    #set the flag to stop the iterations
    iterations = 0
    clustering_changed = True
#    prev_num_cliques = len(cluster_df['Clique'].unique()) + 1
    while clustering_changed:
        # reset the changed flag to false
        clustering_changed = False
        iterations += 1
#        prev_num_cliques = len(cluster_df['Clique'].unique())
#d        done = True
        print("running iteration: " + str(iterations) + ", with " + str(len(cluster_df['Clique'].unique())) + " cliques to further optimize.")
        # cluster the data
        clustering_changed, cluster_df = cluster.build_clusters(cluster_df) 
    #
    print("completed clustering the data by Euclidean distance. ")
    print("Total number of unique cliques clusters generated = " + str(len(cluster_df['Clique'].unique())))
    # write clustered data to CSV file
    print("writing clustered data to a file ./data/tmp_clustered_outfile.csv")
    cluster_df.to_csv('./data/tmp_clustered_outfile.csv',encoding='utf-16',sep='\t')
    print("completed writing clustered events data to the CSV file !")
    #
    return cluster_df
#
# calculate the density of each cluster
def get_densities():
    print("starting to calculate the density and influencer of each cluster")
    density_df = pd.read_csv('./data/tmp_clustered_outfile.csv',encoding='utf-16',sep='\t')
    # remove the column with label unnamed containing index values from CSV
    density_df = density_df[density_df.columns[~density_df.columns.str.contains('Unnamed:')]]
    # drop duplicates
    density_df = density_df.drop_duplicates()
    # append the new column : Density
    density_df['Density'] = -1
    # get the unique clusters
    unique_cl_df = pd.DataFrame(density_df['Clique'].unique())
    # loop through each cluster
    i = 0
    while i <= len(density_df['Clique'].unique())-1:
        # get all the clique specific data
        this_clique_df = pd.DataFrame(density_df.loc[density_df['Clique'] == unique_cl_df[0][i]])
        # calculate the density of the cluster
        this_clique_df = cluster.calculate_density(this_clique_df)
        # update the data-frame with the density
        for index, row in this_clique_df.iterrows():
            density_df['Density'][density_df['UID'] == row['UID']] = float(this_clique_df['Density'].unique())
        #
        i += 1    
    #
    density_df.to_csv('./data/tmp_density_outfile.csv',encoding='utf-16',sep='\t')
    print("completed writing density for the events data to the CSV file !")
    return density_df
#
# drop cliques with less than number
def drop_cliques_of_size(reduced_df,size=1):
    #
    unique_cl_df = pd.DataFrame(reduced_df['Clique'].unique())
    print("starting to drop cluster of size "+str(size)+" from set of "+str(len(unique_cl_df.index))+" clusters.")
    for Ind, row in unique_cl_df.iterrows():
        if len(reduced_df.loc[reduced_df['Clique'] == row[0]]) <= size:
            reduced_df = reduced_df.drop(reduced_df.loc[reduced_df['Clique'] == row[0]].index)
#            print("drop len = " + str(len(df.loc[df['Clique'] == row[0]])))
    reduced_df.to_csv('./data/tmp_cliques_droppedsize.csv',encoding='utf-16',sep='\t')
    print("completed writing " + str(len(reduced_df['Clique'].unique())) + " clusters with size greater than "+str(size) + " to the CSV file !")
    #
    return reduced_df
#
# drop cliques with less than number
def plot_lat_lon_in_catesian(df):
#
#--------------- MAIN CALLS -------------
# map the inputs to the function blocks
# check parameters and echo call functionaX
logstr = "Data filtering parameters: "
if conf.country != "" : logstr += ' country: "' + conf.country + '"'
#else: logstr += " an unspecified country"
if conf.location != "" : logstr += ' location: "' + conf.location + '"'
#else: logstr += " an unspecified location"
if conf.startdate != "" : logstr += ' since: "' + conf.startdate + '"'
#else: logstr += " an unspecified start date"
if conf.enddate != "" : logstr += ' until: "' + conf.enddate + '"'
#else: logstr += " an unspecified end date"
if conf.search != "" : logstr += ' search terms: "' + conf.search + '"'
#else: logstr += " an unspecified keywords"
if conf.maximum > -1 : logstr += ' maximum records: "' + str(conf.maximum) + '"'
else: logstr += " for all records"
print (logstr)
#
# call the function based on the desired data set
data_options = {"twitter" : twitter,
           "ushahidi" : ushahidi,
           "other" : other,           
}
##data = options[conf.source]()
#d density_wise_cluster(data_options[conf.source]())
#data = get_clusters(data_options[conf.source]())
data = pd.DataFrame(get_densities())
data = drop_cliques_of_size(data, 1)
plot.in_catesian(data)
#
#
#
#
# 3. compare data in each cluster to compare anormalies user reporting patterns
# e.g. the behaviour might be to tweet in the evenings on the weekend, then
#      how do the trends in the pre-disaster data differ from the post disaster data

# 4. visually present the data for drawing conclusions or prooving the hypotheses
# e.g. (a) all the cluster color coded by the earliest report received after the desaster
#      (b) clusters with a larger number of behavioural anomalies between pre & post
#      (c) 