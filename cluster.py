# REPAT - CLUSTER
#
# Instructions: 
#     - edit values for the settings in config.py
#     - import (include) this library in main
#
# Reporting Patterns (RePat) for determining telecom availability during crises
# ------------------------------------------------------------------------------
#
# purpose of this code is to build spatial and temporal clusters of telecom availability
#
# contributors: nuwan@lirneasia.net, ilihdian@gmail.com, and 473265320@qq.com
#
# ------------------------------------------------------------------
#
# import libraries
#import sys, os, csv
#import pyquery
import math
import pandas as pd
#import numpy as np
import config as conf
#from jinja2.nodes import Concat
#
# Define global variables
#
n_sph_rad = math.sqrt((conf.maximum_displacement/2)^2 + (conf.maximum_period/2)^2)/2
#
# Define a function to cleanup and ready data for clustering
#
def clean_data(clean_df):
    for index, row in clean_df.iterrows():
        #get rid of the extra chars in string to isolate lat lon in twitter type: Point
        lat = float(row['GPS'].split("[",1)[1].split(",",1)[0])
        lon = float(row['GPS'].split("[",1)[1].split(", ",1)[1].split("]",1)[0])
        #add those decimal coordinates to the dataframe as two columns
        clean_df.set_value(index, 'Latitude', lat)
        clean_df.set_value(index, 'Longitude', lon)
        uid = 's'+str(row['Serial']).zfill(10)
        clean_df.set_value(index, 'UID', uid)
    #remove unnecessary colums from dataframe keep what's necessary
    clean_df['Clique'] = clean_df['UID']
    clean_df = clean_df[['UID','Clique','Username','Date','Geo','Latitude','Longitude','L3','L4']]
    return clean_df
#
# Define a function to calculate the vector Euclidean distance for lat, lon, & time dimensions
#
def vector_distance(lat1, lon1, lat2, lon2, t1, t2):
    earth_radius = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # apply haversine distance formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    #c = 2 * asin(sqrt(a))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    km = earth_radius * c
    #
    # calculate the number of seconds between the two datetimes
    from dateutil import parser
    # calculate time difference in hours
    t = math.fabs((parser.parse(t1) - parser.parse(t2)).total_seconds()) / (60*60*24)
    # return the Euclidean distance
    return(math.sqrt(km**2 + t**2))
#
# Define a function to set the nuclious of the clisque
#
def set_clique_nucleus(clique_df):
    #
    # input dataframe is a subset such that all the records share the same Clique identifier (UID)
    # compute the upper bounds of the N-sphere distance (see config.py for parameter settings)
    # A "clique" comprises a set of vectors that are in a hyper cube; each vector (point) is a neigbour
    # n_sph_rad = math.sqrt((conf.maximum_displacement/2)^2 + (conf.maximum_period/2)^2)/2
    # recalculate the nucleus by finding the central point x with the most number of events within h/2
    # the mean distance of point x to any point y in the set smallest 
    tmp_clique_df = pd.DataFrame(columns=["UID","Avg_Neigbour_Distance"])
    tmp_clique_df['UID'] = clique_df['UID']
    for i, i_row in clique_df.iterrows():
        euclid_dist_sum = 0     # keep sum of the distances to later calculate the mean distance
        events_count = 0     # keep count of the number of records in 
        # setting the j-th point as the core obj calculate the distance to all other events in the clique
        for j, j_row in clique_df.iterrows():
            if i_row['UID'] != j_row['UID']:
                lat1 = clique_df['Latitude'][i]
                lon1 = clique_df['Longitude'][i]
                lat2 = clique_df['Latitude'][j]
                lon2 = clique_df['Longitude'][j]
                t1 = clique_df['Date'][i]
                t2 = clique_df['Date'][j]
                euclid_dist = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
                # calculate the sum of the distances for all the events within the N-sphere
                if (euclid_dist < n_sph_rad):
                    euclid_dist_sum += euclid_dist
                    events_count += 1
        # end the 'j' for loop
        # create a temporary dataframe with the sum of the N-sphere radius to all the j-th event from the i-th nucleus        
        # check if there were any events that were within the spatial and temporal N-sphere
        if events_count > 0 :
            # set the average N-sphere radius
            avg_distance = float(euclid_dist_sum/events_count)
        else :
            # basically set the N-sphere radius to a large number outside of the N-sphere
            avg_distance = float(math.sqrt(conf.maximum_displacement^2 + conf.maximum_period^2))
        #
        # add the average distance to neighbors for the i-th data point
        tmp_clique_df['Avg_Neigbour_Distance'][tmp_clique_df.loc[tmp_clique_df['UID'] == i_row['UID']].index] = avg_distance

    # end the 'i' for loop
    # update the new This Clique Nucleus with the j-th Nucleus with smallest average N-sphere radius to all neighbors
    clique_df['Clique'] = tmp_clique_df['UID'][tmp_clique_df['Avg_Neigbour_Distance'].argmin()]
    return clique_df
#
# Define a function to remove all symbol characters and replace with a space 
#
def build_clusters(df):
    #set the flag to stop the iterations
#    iterations = 0
    clique_changed = False
#    while not done:
#        iterations += 1
#        done = True
#        print("Processing iteration: " + str(iterations) + ", has " + str(len(df['Clique'].unique())) + " cliques.")
        # loop through all individual records to ensure they are assigned to a clique
    i = 0
#d        print('{0}\r'.format("trying to assign the Clique (UID) for all cliques ...")),
#d        print("trying to assign the Clique (UID) for all cliques ...")
    while i <= len(df.index)-1:
        # get all the data belonging to the clique of the i-th record
        this_clique_df = pd.DataFrame()
        this_clique_df = df.loc[df['Clique'] == df['Clique'][i]]
        # get the revised or same Clique (fk:UID) for this clique
        this_clique_df = set_clique_nucleus(this_clique_df)
        # update original data-frame with changes
        for ind, row in this_clique_df.iterrows():
            df['Clique'][df.loc[df['UID'] == row['UID']].index] = row['Clique']
        #
        print('{0}\r'.format("polling events to pull into clique " + df['Clique'][i])),
        j = 0
        next_clique_df = pd.DataFrame()
        # loop through cliques to lure in other neihbourhood events into the i-th clique
        while j <= len(df.index)-1:
#           print("i = " + str(i) + ", j = " + str(j))
            # get the j-th clique (only process cliques where i is not equal to j)
            next_clique_df = df.loc[df['Clique'] == df['Clique'][j]]
            # skip the rest if i-th and j-th clique are the same
            if next_clique_df['Clique'].unique().any() != this_clique_df['Clique'].unique().any():
                #
                k = 0
                while k <= len(next_clique_df.index)-1:
#                   print('{0}\r'.format("now processing "+"UID("+str(i)+")="+df.iloc[i]["UID"]+" UID("+str(j)+")="+df.iloc[j]["UID"]+" UID("+str(k)+")="+next_clique_df.iloc[k]["UID"])),
#                   print("UID(i)="+df.iloc[i]["UID"]+" UID(j)="+df.iloc[j]["UID"]+" UID(k)="+next_clique_df.iloc[k]["UID"])
                    # re-assign the clique nucleus for the latest clique
                    # i.e. there might be a better data point to serve as the central point (nucleus)
                    next_clique_df = set_clique_nucleus(next_clique_df)
                    # update original data-frame with changes
                    for index, row in next_clique_df.iterrows():
                        df['Clique'][df.loc[df['UID'] == row['UID']].index] = row['Clique']
                    #
                    # refresh the next clique in the list with latest clique data
                    next_clique_df = pd.DataFrame()
                    next_clique_df = df.loc[df['Clique'] == df['Clique'][j]]
                    #next_clique_df.drop_duplicates()
                    #get the Nucleus UID for the i-th and j-th cliques
                    next_nucleus = next_clique_df['Clique'].unique()
                    this_nucleus = this_clique_df['Clique'].unique()
                    # calculate N-sphere radius for both this event and next event, relative to their
                    # commonly shared clique nucleus. lat1 & lon1 are coordinates of the nuclues
                    # lat2 & lon2 are coordinates of the k-th event in j-th clique (next)
                    # t1 is the datetime of the k-th event in clique j clique (next)
                    # t2 is the datetime of the Nucleus
                    tmpdf = pd.DataFrame()
                    tmpdf = this_clique_df.loc[this_clique_df['UID'] == this_nucleus[0]]
                    lat1 = float(tmpdf.iloc[0]['Latitude'])
                    lon1 = float(tmpdf.iloc[0]['Longitude'])
                    t1 = tmpdf.iloc[0]['Date']     # have to do it this long way due to various errors
                    lat2 = float(next_clique_df.iloc[k]['Latitude'])
                    lon2 = float(next_clique_df.iloc[k]['Longitude'])
                    t2 = next_clique_df.iloc[k]['Date']
                    this_clique_distance = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
                    #
                    # calculate N-sphere radius for both next event Nucleus and next event 
                    # lat1 & lon1 are coordinates of the nuclues
                    # lat2 & lon2 are coordinates of the k-th event in j-th clique (next)
                    # t1 is the datetime of the k-th event in clique j clique (next)
                    # t2 is the datetime of the Nucleus
                    tmpdf = pd.DataFrame()
                    tmpdf = next_clique_df.loc[next_clique_df['UID'] == next_nucleus[0]]
                    lat1 = float(tmpdf.iloc[0]['Latitude'])
                    lon1 = float(tmpdf.iloc[0]['Longitude'])
                    t1 = tmpdf.iloc[0]['Date']
                    lat2 = float(next_clique_df.iloc[k]['Latitude'])
                    lon2 = float(next_clique_df.iloc[k]['Longitude'])
                    t2 = next_clique_df.iloc[k]['Date']
                    next_clique_distance = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
                    #
                    # check whether the comparing (next) clique has more than one element
                    # if it does then compare which is shorter N-sphere radius to this clique nucleus
                    # or N-sphere radius to own clique nucleus; to change cliques
                    # if clique has only one data point then automatically add to this clique
                    # provided the the N-sphere radius is within the N-sphere radius bound
                    if len(next_clique_df.index) > 1:
                        # check if the next data is closer to this clique nucleus or not
                        if this_clique_distance < n_sph_rad and this_clique_distance < next_clique_distance:
                            clique_changed = True
                            # change the clique value of the next clique data point to this clique value in main dataframe
                            next_clique_df['Clique'][j] = this_nucleus[0]
#                               print('{0}\r'.format("Adding data point: "+next_clique_df.iloc[k]['UID']+" from clique: "+next_nucleus[0]+" to clique: "+this_nucleus[0])),
                            df.loc[df['UID'] == next_clique_df['UID'][j]] = next_clique_df.loc[next_clique_df.index[k]].values
                            #this_clique_df.loc[len(this_clique_df)] = next_clique_df.loc[next_clique_df.index[k]].values
                            #df.reset_index()
                    # only has only one data point, then add to the clique
                    else:
                        # if and only if N-sphere radius satisfies maximum radius constratint
                        if this_clique_distance < n_sph_rad:
                            clique_changed = True
                            # change the clique value of the next clique data point to this clique value in main dataframe
                            next_clique_df['Clique'][j] = this_nucleus[0]
#                           print('{0}\r'.format("Adding a single data point clique: "+next_clique_df.iloc[k]['UID']+" to clique: "+this_nucleus[0])),
                            df.loc[df['UID'] == next_clique_df['UID'][j]] = next_clique_df.loc[next_clique_df.index[k]].values
                    # update the next clique to reflect the new changes; 
                    # especially if k-th element clique was change to this clique
                    next_clique_df = pd.DataFrame()
                    next_clique_df = df.loc[df['Clique'] == df['Clique'][j]]
                    #
                    # increment k to the next (check if it misses an data record)
                    k += 1
            #        
            # increment j to fetch the next clique
            j += 1
        #    
        # go to the next event to iterate process again
        i += 1
#        print("presently generated number of unique cliques = " + str(len(df['Clique'].unique())))
        df.to_csv('./data/tmp_clustered_outfile.csv',encoding='utf-16',sep='\t')
#    print(str(i) + " events (dataframe records) assigned to distinct cliques !")
    #
    return clique_changed,df
#
# Define a function to calculate the density of a cluster 
#
def calculate_density(df):
    # get the nucleus
    nucleus_df = df.loc[df['Clique'] == df['UID']]
    # lat, lon, date of the nucleus (or attractor) data
    lat1 = float(nucleus_df.iloc[0]['Latitude'])
    lon1 = float(nucleus_df.iloc[0]['Longitude'])
    t1 = nucleus_df.iloc[0]['Date']
    # loop through the clique to calculate the Gaussian sum
    j = 0
    for index, row in df.iterrows():
        # get the revised or same Clique (fk:UID) for this clique
        lat2 = float(row['Latitude'])
        lon2 = float(row['Longitude'])
        t2 = row['Date']
        df['Density'][df.index == index] = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
    #
    # calculate the standard deviation for the clique data N-Sphere Distances
    gaussian_sum = 0
    # check if more than one distinct event
    if df['Density'].std() > 0:
        for index, row in df.iterrows():
            gaussian_sum += math.exp(-1*float(row['Density'])/(2*df['Density'].std()))
        # deduct 1 to compensate for calculating the gaussian for the nucleus; i.e. exp(0) = 1
        df['Density'] = gaussian_sum - 1
    else:
        #a clique with single event or multiples identical events
        df['Density'] = gaussian_sum
    #   
    # return the data-frame with the density
    return df