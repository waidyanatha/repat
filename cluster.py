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
import config as conf
#
# Define global variables
#
n_sph_rad = math.sqrt((conf.maximum_displacement/2)^2 + (conf.maximum_period/2)^2)/2
spatia_distance = conf.maximum_displacement
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
    if str(t1) != str(t2):
        t = math.fabs((parser.parse(t1) - parser.parse(t2)).total_seconds()) / (60*60*24)
    else:
        t=0
    # return the Euclidean distance
    return(math.sqrt(km**2 + t**2))
#
# Define a function to set the nuclious of the clisque
#
def set_clique_density_attractor(clique_df):
    #
    # input dataframe is a subset such that all the records share the same Clique identifier (UID)
    # compute the upper bounds of the N-sphere distance (see config.py for parameter settings)
    # A "clique" comprises a set of vectors that are in a hyper cube; each vector (point) is a neigbour
    # n_sph_rad = math.sqrt((conf.maximum_displacement/2)^2 + (conf.maximum_period/2)^2)/2
    # recalculate the attractor by finding the central point x with the most number of events within h/2
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
        # create a temporary dataframe with the sum of the N-sphere radius to all the j-th event from the i-th attractor        
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
    # update the new This Clique attractor with the j-th attractor with smallest average N-sphere radius to all neighbors
    clique_df['Clique'] = tmp_clique_df['UID'][tmp_clique_df['Avg_Neigbour_Distance'].argmin()]
    return clique_df
#
# Define a function to manage a list of all clique nuclei that have been polled
#
def poll_this_cliques(polled_cliques_df, old_attractor, new_attractor):
    #
    # set a flag whether or not to test this attractor
    test_attractor = False
    # check if this clique attractor is already in the tested list
    if len(polled_cliques_df) > 0:
        if polled_cliques_df.loc[polled_cliques_df['Clique'] == old_attractor[0]].empty:
            # if not in the list then add to the list
            polled_cliques_df = polled_cliques_df.set_value(len(polled_cliques_df), 'Clique', old_attractor[0])
            polled_cliques_df = polled_cliques_df.reset_index(drop=True)
            # was not in list so test it
            test_attractor = True
        else:
            # it is in the list hence skip testing this clique
            # first remove the old attractor
            polled_cliques_df = polled_cliques_df.drop(polled_cliques_df.loc[polled_cliques_df['Clique'] == old_attractor[0]].index)
            polled_cliques_df = polled_cliques_df.reset_index(drop=True)
            # now add the new attractor, which might be the same as the old attractor but that's OK
            polled_cliques_df = polled_cliques_df.set_value(len(polled_cliques_df), 'Clique', new_attractor[0])
            test_attractor = False
    else:
        # its the first attractor so add it to the tested list
        polled_cliques_df = polled_cliques_df.set_value(len(polled_cliques_df), 'Clique', old_attractor[0])
        polled_cliques_df = polled_cliques_df.reset_index(drop=True)
        # since its the first it should be tested
        test_attractor = True
        
##D    # first remove the old attractor
##D    polled_cliques_df = polled_cliques_df.drop(polled_cliques_df.loc[polled_cliques_df['Clique'] == old_attractor[0]].index)
##D    polled_cliques_df.reset_index(drop=True)
##D    # now add the new attractor, which might be the same as the old attractor but that's OK
##D    polled_cliques_df = polled_cliques_df.set_value(len(polled_cliques_df), 'Clique', new_attractor[0])
    
    return test_attractor, polled_cliques_df
#
# Define a function to remove all symbol characters and replace with a space 
#
def build_clusters(df):
    #set the flag to stop the iterations
#    iterations = 0
    clique_changed = False
    i = 0
    clique_tested_df = pd.DataFrame(columns=["Clique"])
    while i <= len(df['Clique'].unique())-1:
        # get all the data belonging to the clique of the i-th record
        this_clique_df = pd.DataFrame(df.loc[df['Clique'] == df['Clique'][i]])
        this_attractor_old =  this_clique_df['Clique'].unique()
        # re-calculate and set the attractor for this clique
        this_clique_df = set_clique_density_attractor(this_clique_df)
        this_attractor_new = this_clique_df['Clique'].unique()
        # update original data-frame with changes
        for index, row in this_clique_df.iterrows():
            df['Clique'][df.loc[df['UID'] == row['UID']].index] = row['Clique']
        # check if this clique attractor is already in the tested list
        test_this_clique, clique_tested_df = poll_this_cliques(clique_tested_df, this_attractor_old, this_attractor_new)
        if test_this_clique == True:
            #
            print('{0}\r'.format("for i = "+str(i)+" of "+str(len(df['Clique'].unique()))+"  cliques, polling data to pull into clique " + df['Clique'][i])),
            j = 0
            next_clique_df = pd.DataFrame()
            # loop through cliques to lure in other neighborhood events into the i-th clique
            while j <= len(df['Clique'].unique())-1:
                # get the j-th clique (only process cliques where i is not equal to j)
                next_clique_df = df.loc[df['Clique'] == df['Clique'][j]]
                # skip the rest if i-th and j-th clique are the same
                if next_clique_df['Clique'].unique().any() != this_clique_df['Clique'].unique().any():
                    #
                    k = 0
                    while k <= len(next_clique_df.index)-1:
                        # re-assign the clique attractor for the latest clique
                        # i.e. there might be a better data point to serve as the central point (attractor)
                        next_clique_df = set_clique_density_attractor(next_clique_df)
                        # update original data-frame with changes
                        for index, row in next_clique_df.iterrows():
                            df['Clique'][df.loc[df['UID'] == row['UID']].index] = row['Clique']
                        #
                        # refresh the next clique in the list with latest clique data
                        next_clique_df = pd.DataFrame()
                        next_clique_df = df.loc[df['Clique'] == df['Clique'][j]]
                        #get the attractor UID for the i-th and j-th cliques
                        next_attractor = next_clique_df['Clique'].unique()
                        this_attractor = this_clique_df['Clique'].unique()
                        #
                        # calculate N-sphere radius for both this event and next event, relative to their
                        # commonly shared clique attractor. lat1 & lon1 are coordinates of the attractor
                        # lat2 & lon2 are coordinates of the k-th event in j-th clique (next)
                        # t1 is the datetime of the k-th event in clique j clique (next)
                        # t2 is the datetime of the attractor
                        tmpdf = pd.DataFrame()
                        tmpdf = this_clique_df.loc[this_clique_df['UID'] == this_attractor[0]]
                        lat1 = float(tmpdf.iloc[0]['Latitude'])
                        lon1 = float(tmpdf.iloc[0]['Longitude'])
                        t1 = tmpdf.iloc[0]['Date']     # have to do it this long way due to various errors
                        lat2 = float(next_clique_df.iloc[k]['Latitude'])
                        lon2 = float(next_clique_df.iloc[k]['Longitude'])
                        t2 = next_clique_df.iloc[k]['Date']
                        this_clique_distance = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
                        #
                        # calculate N-sphere radius for both next event attractor and next event 
                        # lat1 & lon1 are coordinates of the nuclues
                        # lat2 & lon2 are coordinates of the k-th event in j-th clique (next)
                        # t1 is the datetime of the k-th event in clique j clique (next)
                        # t2 is the datetime of the attractor
                        tmpdf = pd.DataFrame()
                        tmpdf = next_clique_df.loc[next_clique_df['UID'] == next_attractor[0]]
                        lat1 = float(tmpdf.iloc[0]['Latitude'])
                        lon1 = float(tmpdf.iloc[0]['Longitude'])
                        t1 = tmpdf.iloc[0]['Date']
                        lat2 = float(next_clique_df.iloc[k]['Latitude'])
                        lon2 = float(next_clique_df.iloc[k]['Longitude'])
                        t2 = next_clique_df.iloc[k]['Date']
                        next_clique_distance = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
                        #
                        # check whether the comparing (next) clique has more than one element
                        # if it does then compare which is shorter N-sphere radius to this clique attractor
                        # or N-sphere radius to own clique attractor; to change cliques
                        # if clique has only one data point then automatically add to this clique
                        # provided the the N-sphere radius is within the N-sphere radius bound
                        if len(next_clique_df.index) > 1:
                            # check if the next data is closer to this clique attractor or not
                            if this_clique_distance < n_sph_rad and this_clique_distance < next_clique_distance:
                                clique_changed = True
                                # change the clique value of the next clique data point to this clique value in main dataframe
                                next_clique_df['Clique'][j] = this_attractor[0]
#                                print('{0}\r'.format("Adding data point: "+next_clique_df.iloc[k]['UID']+" from clique: "+next_attractor[0]+" to clique: "+this_attractor[0])),
                                df.loc[df['UID'] == next_clique_df['UID'][j]] = next_clique_df.loc[next_clique_df.index[k]].values
                        # only has only one data point, then add to the clique
                        else:
                            # if and only if N-sphere radius satisfies maximum radius constratint
                            if this_clique_distance < n_sph_rad:
                                clique_changed = True
                                # change the clique value of the next clique data point to this clique value in main dataframe
                                next_clique_df['Clique'][j] = this_attractor[0]
#                               print('{0}\r'.format("Adding a single data point clique: "+next_clique_df.iloc[k]['UID']+" to clique: "+this_attractor[0])),
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
#d        else:
#d            print("skip this new clique "+this_attractor_new+" and old clique "+this_attractor_old)
        i += 1
#        print("presently generated number of unique cliques = " + str(len(df['Clique'].unique())))
        df.to_csv('./data/tmp_clustered_outfile.csv',encoding='utf-16',sep='\t')
#    print(str(i) + " events (dataframe records) assigned to distinct cliques !")
    #
    return clique_changed,df
#
# Define a function to calculate the density of a cluster 
#
def calculate_cluster_density(df):
    # get the attractor
    attractor_df = df.loc[df['Clique'] == df['UID']]
    # lat, lon, date of the attractor (or attractor) data
    lat1 = float(attractor_df.iloc[0]['Latitude'])
    lon1 = float(attractor_df.iloc[0]['Longitude'])
    t1 = attractor_df.iloc[0]['Date']
    # loop through the clique to calculate the Gaussian sum
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
        # deduct 1 to compensate for calculating the gaussian for the attractor; i.e. exp(0) = 1
        df['Density'] = gaussian_sum - 1
    else:
        #a clique with single event or multiples identical events
        df['Density'] = gaussian_sum
    #   
    # return the data-frame with the density
    return df
#
# Define function to give single cluster and find the nearest neighbor from a data frame of clusters
#
def get_nearest_cluster_neighbor(this_clique_row, neighbor_df):
    #
    if this_clique_row.empty and neighbor_df.empty:
        print("NO data to process")
        return None
    #
    lat1 = float(this_clique_row['Latitude'])
    lon1 = float(this_clique_row['Longitude'])
    t1 = this_clique_row['Date']
#    old_neighbor_distance = float(spatia_distance)
    # loop through the data frame of clusters to find nearest neighbor
    unique_cliques_df = pd.DataFrame(neighbor_df['Clique'].unique())
    for row_index, unique_clique_id in unique_cliques_df.iterrows():
        # initialize a data frame to store all the nearest neighbors
        this_clique_neighbors_df = pd.DataFrame(columns=['Clique','Neighbors','Date','Density', 'Longitude','Latitude'])
        # get the lat, lon values for the two data rows
        other_clique_df = pd.DataFrame(neighbor_df.loc[neighbor_df['UID'] == unique_clique_id[0]])
        lat2 = float(other_clique_df['Latitude'])
        lon2 = float(other_clique_df['Longitude'])
        t2 = t1     #to set the time difference to 0, we only need the spatial distance
        new_neighbor_distance = vector_distance(lat1, lon1, lat2, lon2, t1, t2)
        #
        # check if the distance is closer than the previous or not
        if float(new_neighbor_distance) < float(spatia_distance):
            next_index = len(this_clique_neighbors_df)
            this_clique_neighbors_df.set_value(next_index, 'Clique', this_clique_row.iloc[0]['Clique'])
            this_clique_neighbors_df.set_value(next_index, 'Neighbors', other_clique_df.iloc[0]['Clique'])
            this_clique_neighbors_df.set_value(next_index, 'Date', this_clique_row.iloc[0]['Date'])
            this_clique_neighbors_df.set_value(next_index, 'Density', float(this_clique_row.iloc[0]['Density']))
            this_clique_neighbors_df.set_value(next_index, 'Longitude', float(this_clique_row.iloc[0]['Longitude']))
            this_clique_neighbors_df.set_value(next_index, 'Latitude', float(this_clique_row.iloc[0]['Latitude']))
    #
    return this_clique_neighbors_df
        
