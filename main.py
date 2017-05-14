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
import datetime as dt
from sklearn.cluster import KMeans
from pandas.core.series import Series
import math
#
######################################################################################
#
# INITIALIZE: set auxiliary directories and paths
#
######################################################################################
def initiatlize():
    #
    # plots directory
    dir_path = "./plots/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # data directory
    dir_path = "./data/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    #
    # check parameters and echo call functionaX
    logstr = "Data filtering parameters: \n"
    if conf.ISO_3166_1_APLPHA_2 != "" : logstr += ' ISO 3166-1 APLPHA-2 = "' + conf.ISO_3166_1_APLPHA_2 + '"\n'
    #else: logstr += " an unspecified country"
    if conf.location != "" : logstr += ' Epicenter           = "' + conf.location + '"\n'
    #else: logstr += " an unspecified location"
    if conf.startdate != "" : logstr += ' From                = "' + conf.startdate + '"\n'
    #else: logstr += " an unspecified start date"
    if conf.enddate != "" : logstr += ' Until               = "' + conf.enddate + '"\n'
    #else: logstr += " an unspecified end date"
    if conf.search != "" : logstr += ' Search terms        = "' + conf.search + '"\n'
    #else: logstr += " an unspecified keywords"
    if conf.maximum > -1 : logstr += ' Maximum records     = "' + str(conf.maximum) + '"\n'
    else: logstr += " for all records"
    print (logstr)
#
######################################################################################
#
# Extract geospatial data from various sources
#
######################################################################################
def twitter():
    print("retrieving twitter data from http://www.twitter.com")
    df = rio.get_old_tweets(conf.startdate,conf.enddate,conf.search,conf.maximum)
    print("writing twitter data to ./data/"+conf.file_raw_extract_data+" !")
    df = df.reset_index(drop=True)
    df.to_csv("./data/"+conf.file_raw_extract_data,encoding='utf-16',sep='\t')    
    print("twitter extraction complete!")
    return df
#
def ushahidi():
    print ("ushahidi\n")

def other():
    print ("other\n")

######################################################################################
# 
# Cluster the date set by geographic location and time proximity
#
######################################################################################
def get_clusters(cluster_df):
    print("starting to cluster the event data ...")
#        print('{0}\r'.format("trying to cleanup and format all data ...")),
    #
    if cluster_df.columns.str.contains('Unnamed:').any():
        cluster_df = cluster_df[cluster_df.columns[~cluster_df.columns.str.contains('Unnamed:')]]
    #
    print("first cleanup and format data to stage for clustering ...")
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
    cluster_df = cluster_df.reset_index(drop=True)
    cluster_df.to_csv("./data/"+conf.file_clustered_data,encoding='utf-16',sep='\t')
    print("completed writing clustered events data to  ./data/"+conf.file_clustered_data+" !")
    #
    return cluster_df
######################################################################################
#
# calculate the density of each cluster based on the Gaussian function
#
######################################################################################
def get_densities(density_df):
    #
    print("starting to calculate the density and influencer of each cluster")
    #
#d    density_df = pd.read_csv('./data/tmp_clustered_outfile.csv',encoding='utf-16',sep='\t')
    # remove the column with label unnamed containing index values from CSV
    if density_df.columns.str.contains('Unnamed:').any():
        density_df = density_df[density_df.columns[~density_df.columns.str.contains('Unnamed:')]]
    #
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
        this_clique_df = cluster.calculate_cluster_density(this_clique_df)
        # update the data-frame with the density
        for index, row in this_clique_df.iterrows():
            density_df['Density'][density_df['UID'] == row['UID']] = float(this_clique_df['Density'].unique())
        #
        i += 1    
    #
    density_df = density_df.reset_index(drop=True)
    density_df.to_csv("./data/"+conf.file_density_data,encoding='utf-16',sep='\t')
    print("completed writing density data to  ./data/"+conf.file_density_data+" !")
    return density_df
######################################################################################
#
# drop cliques with less than N number of event data in the clique
#
######################################################################################
def drop_cliques_of_size(reduced_df,size=1):
    #
    if reduced_df.columns.str.contains('Unnamed:').any():
        reduced_df = reduced_df[reduced_df.columns[~reduced_df.columns.str.contains('Unnamed:')]]
    #
    unique_cl_df = pd.DataFrame(reduced_df['Clique'].unique())
    print("starting to drop cluster of size "+str(size)+" from set of "+str(len(unique_cl_df.index))+" clusters.")
    for Ind, row in unique_cl_df.iterrows():
        if len(reduced_df.loc[reduced_df['Clique'] == row[0]]) <= size:
            reduced_df = reduced_df.drop(reduced_df.loc[reduced_df['Clique'] == row[0]].index)
#            print("drop len = " + str(len(df.loc[df['Clique'] == row[0]])))
    reduced_df = reduced_df.reset_index(drop=True)
    reduced_df.to_csv("./data/"+conf.file_no_noise_data,encoding='utf-16',sep='\t')
    print("completed writing "+str(len(reduced_df['Clique'].unique()))+" clusters with size greater than "+str(size)+" to ./data/"+conf.file_no_noise_data+" !")
    #
    return reduced_df
######################################################################################
#
# plot the clusters on maps and cartesian planes
#
######################################################################################
def plot_all_clusters_before_after(plot_df):
    #
    if plot_df.columns.str.contains('Unnamed:').any():
        plot_df = plot_df[plot_df.columns[~plot_df.columns.str.contains('Unnamed:')]]
    #
    axis_list = ["Latitude","Longitude"]
    plot_df = plot_df.loc[plot_df['Clique'] == plot_df['UID']]

    # create data-frame with before
    before_df = pd.DataFrame(plot_df.loc[plot_df['Date'] < conf.event_datetime])
    if not before_df.empty:
        print("starting plot cluster lat/lon data before "+str(conf.event_datetime)+" on a cartesian plane.")
        title = "Lat vs. Lon plot of clusters before: "+str(conf.event_datetime)
        plot.catesian_plane(before_df, axis_list, title, "plot_cartesian_plane_before.png")
        print("starting plot "+ str(len(before_df['Clique'].unique())) +" cluster lat/lon data before "+str(conf.event_datetime)+" on a map.")
        title = "Map plot of clusters before: "+str(conf.event_datetime)
        plot.map_points(before_df, axis_list, title, "plot_map_before.png")
    else:
        print("No data found before "+str(conf.event_datetime))
    # create data-frame with after
    after_df = pd.DataFrame(plot_df.loc[plot_df['Date'] >= conf.event_datetime])
    if not after_df.empty:
        print("starting plot "+ str(len(after_df['Clique'].unique())) +" cluster lat/lon data after "+str(conf.event_datetime)+" on a cartesian plane.")
        title = "Lat vs. Lon plot of clusters after: "+str(conf.event_datetime)
        plot.catesian_plane(after_df, axis_list, title, "plot_cartesian_plane_after.png")
        print("starting plot cluster lat/lon coordinates, data after "+str(conf.event_datetime)+" on a map.")
        title = "Map plot of clusters after: "+str(conf.event_datetime)
        plot.map_points(after_df, axis_list,title, "plot_map_after.png")
    else:
        print("No data found after "+str(conf.event_datetime))
        
    # calculate and plot the delayed reporting time correlation
    print("Completed plotting cluster data !")
    #
    return 0
#
######################################################################################
#
# BEFORE AFTER COMPARISON: plot after incident data in the neighborhood of data before 
# 
######################################################################################
#
def plot_cluster_comparison_before_after(cluster_df):
    print("Starting process to compare before and after data to assign nearest neighbor cluster")
    if cluster_df.columns.str.contains('Unnamed:').any():
        cluster_df = cluster_df[cluster_df.columns[~cluster_df.columns.str.contains('Unnamed:')]]
    #
    cluster_df['Neighbor'] = None
    nearest_neighbors_df = pd.DataFrame(columns=['Clique','Neighbors','Date','Density','Longitude','Latitude'])
    # separate the data
    after_df = pd.DataFrame(cluster_df.loc[cluster_df['Date'] >= conf.event_datetime])
    before_df = pd.DataFrame(cluster_df.loc[cluster_df['Date'] < conf.event_datetime])
    if after_df.empty or before_df.empty:
        print("No distinct before and after datasets to assign before cluster neighbors to after clusters")
        return 0
    # data available proceed to compute which after clusters intersect with after clusters
    unique_after_cliques = pd.DataFrame(after_df['Clique'].unique())
    for row_index, clique_id in unique_after_cliques.iterrows():
        # get the clique data points
        this_after_clique = pd.DataFrame(cluster_df.loc[cluster_df['UID'] == clique_id[0]])
        this_clique_neighbors = cluster.get_nearest_cluster_neighbor(this_after_clique,before_df)
        if not this_clique_neighbors.empty:
            for clique_index, clique_row in this_clique_neighbors.iterrows():
                next_index = len(nearest_neighbors_df)
                nearest_neighbors_df.set_value(next_index, 'Clique', clique_row['Clique'])
                nearest_neighbors_df.set_value(next_index, 'Neighbors', clique_row['Neighbors'])
                nearest_neighbors_df.set_value(next_index, 'Date', clique_row['Date'])
                nearest_neighbors_df.set_value(next_index, 'Density', clique_row['Density'])
                nearest_neighbors_df.set_value(next_index, 'Longitude', clique_row['Longitude'])
                nearest_neighbors_df.set_value(next_index, 'Latitude', clique_row['Latitude'])
    #
    #plot the data on a map
    print("starting plot clusters with data before and after comparison "+str(conf.event_datetime)+" on a map.")
    axis_list = ["Latitude","Longitude"]
    title = "Clusters After: "+str(conf.event_datetime+" Nearest to Neighbors Before ")
    plot.map_points(nearest_neighbors_df, axis_list,title, "plot_map_before_after_comparison.png")
    #
    #plot the data in a time series
    plot.time_series_points(nearest_neighbors_df, axis_list, title, "plot_timeseries_before_after_comparison.png")
    #
    print("Completed plotting before and after comparison !")    
    return 0
#
######################################################################################
#
# REPORTING DELAYS: calculate and plot the delayed reporting time for each cluster on a map
# 
######################################################################################
#
def plot_reporting_delays(plot_df):
    #
    if plot_df.columns.str.contains('Unnamed:').any():
        plot_df = plot_df[plot_df.columns[~plot_df.columns.str.contains('Unnamed:')]]
    #
    delay_df = pd.DataFrame(columns=['Series','Clique','Date','Delay', 'Density', 'Longitude', 'Latitude', 'K_means'])
    after_df = pd.DataFrame(plot_df.loc[plot_df['Date'] >= conf.event_datetime])
    if not after_df.empty:
        print("starting plot "+ str(len(after_df['Clique'].unique())) +" cluster reporting delays after "+str(conf.event_datetime)+" on a cartesian plane.")
        unique_cliques = pd.DataFrame(after_df['Clique'].unique())
        for row_index, row in unique_cliques.iterrows():
            # get the clique data points
            this_clique_df = pd.DataFrame(after_df.loc[after_df.Clique == row[0]])
            # get the most recent date
            #smallest_dt = this_clique_df['Date'][this_clique_df['Date'].argmin()]
            smallest_dt = pd.Timestamp(this_clique_df['Date'].min())
            event_dt = pd.Timestamp(conf.event_datetime)
            num_of_hours = float((smallest_dt - event_dt).days)*24 + float((smallest_dt - event_dt).seconds)/(60*60)
            # retrieve the longitude and latitude
            den = float(this_clique_df['Density'].loc[this_clique_df['UID'] == row[0]])
            lon = float(this_clique_df['Longitude'].loc[this_clique_df['UID'] == row[0]])
            lat = float(this_clique_df['Latitude'].loc[this_clique_df['UID'] == row[0]])
            # test if number of hours are beyond the maximum period after the hazard event
            if num_of_hours > conf.maximum_period:
                index_value = len(delay_df)
                delay_df.set_value(index_value, 'Series', int(index_value))
                delay_df.set_value(index_value, 'Clique', row[0])
                delay_df.set_value(index_value, 'Date', smallest_dt)
                delay_df.set_value(index_value, 'Delay', num_of_hours)
                delay_df.set_value(index_value, 'Longitude', lon)
                delay_df.set_value(index_value, 'Latitude', lat)
        # compute the number of clusters 'k' based on 24 hour intervals
        k = math.ceil((delay_df.loc[:,'Delay'].max() - delay_df.loc[:,'Delay'].min()))
        # can we divide into 24 hour intervals
        if k/24 > 1:
            k = math.floor(k/24)
        # otherwise set k to be one hour
        else:
            k = math.floor(k)
        # set k to be less than 23 colors
        if k > 23:
            k = int(23)
        # k-means clustering of the delays to assign a color
        X = delay_df[['Delay','Delay']].as_matrix(columns=None)
        km = KMeans(n_clusters=int(k), init='k-means++', n_init=10, max_iter=300, tol=0.0001, random_state=None, 
                    precompute_distances='auto', verbose=0, copy_x=True, n_jobs=1, algorithm='auto')
        km.fit(X)
        predict=km.predict(X)
        delay_df['K_means'] = Series(predict,index=delay_df.index)
#d        delay_df['Color'] = Series(predict,index=delay_df.index)
        # plot delays in a cartesian plane
        title = "Cluster-wise reporting delays after : "+str(conf.event_datetime)
        axis_list = ["Series","Delay"]
        file = "plot_cartesian_reporting_delays.png"
        plot.scatter_plane(delay_df, axis_list, title, file)
        # plot delays on a map
        axis_list = ["Longitude","Latitude"]
        file = "plot_map_reporting_delays.png"
        plot.scatter_map(delay_df, axis_list, title, file)
    #
    return 0
#
######################################################################################
#
# REPORTING TIME SERIEs: plot the time series for nearest neighbor geographic clusters
# 
######################################################################################
#
def plot_nearest_neighbor_timeseries(plot_df):
    print("starting to build nearest neighbor cluster time series ...")
    #set the flag to stop the iterations
    iterations = 0
    clustering_changed = True
    while clustering_changed:
        # reset the changed flag to false
        clustering_changed = False
        iterations += 1
        print("running iteration: " + str(iterations) + ", with " + str(len(plot_df['Clique'].unique())) + " cliques to further optimize.")
        # cluster the data
        clustering_changed, plot_df = cluster.build_nearest_neighbor_timeseries(plot_df) 
    #
    print("completed clustering the data by geographic distance. ")
    print("Total number of unique cliques clusters generated = " + str(len(plot_df['Clique'].unique())))
    # write clustered data to CSV file
    print("writing clustered data to a file ./data/tmp_clustered_outfile.csv")
    plot_df.to_csv('./data/tmp_nearest_neighbor_cluster_ts.csv',encoding='utf-16',sep='\t')
    print("completed writing clustered events data to the CSV file !")
    #
    event_dt = pd.Timestamp(conf.event_datetime)
    unique_cliques = pd.DataFrame(plot_df['Clique'].unique())
    for row_index, row in unique_cliques.iterrows():
        # get the clique data points
        this_clique_df = pd.DataFrame(plot_df.loc[plot_df.Clique == row[0]])
        this_clique_df['TS'] = None
        #plot the data on a map
        print("starting plot time series for cluster "+row[0])
        axis_list = ["Density","TS"]
        title = "Time Series for CLuster "+row[0]
        fname = "plot_timeseries_"+row[0]+".png"
        #
        for this_row_index, this_row in this_clique_df.iterrows():
            #
            this_dt = pd.Timestamp(this_row['Date'])
            num_of_hours = float((this_dt - event_dt).days)*24
            this_clique_df.set_value(this_row_index, 'TS', num_of_hours)
        #
        #plot the data in a time series
        plot.time_series_points(this_clique_df, axis_list, title, fname)
    #
    print("Completed plotting time series data !")    

    #
    return 0
#
######################################################################################
#
#    MAIN CALLS 
#
######################################################################################
tstart = dt.datetime.now()
print("starting RePat at "+str(tstart))
#
print("initializing repat ")
initiatlize()
# call the function based on the desired data set
data_options = {"twitter" : twitter,
           "ushahidi" : ushahidi,
           "other" : other,           
}
# retrieve the data from defined source
data = pd.DataFrame(data_options[conf.source]())
if not data.empty:
    print("Data retrieved with "+str(len(data))+" - "+conf.source+" records")
#d    data = get_clusters(data_options[conf.source]())
    #
    #######################################
    # CLUSTER THE DATA
    #######################################
    # INSTRUCTION: uncomment the below code line only if you want to read from file to reduce time
    #if not os.path.exists("./data/"+conf.file_formatted_data):
    #    print("./data/"+conf.file_formatted_data+" does not exist!")
    #else:
    #    print("loading formatted data from file to skip retrieving data: ./data/"+conf.file_formatted_data)
    #    data=pd.read_csv("./data/"+conf.file_formatted_data,encoding='utf-16',sep='\t') 
    data = pd.DataFrame(get_clusters(data))
    #
    #######################################
    # DENSITY-WISE CLUSTER
    #######################################
    # INSTRUCTION: uncomment the below code line only if you want to read from file to reduce time
    #if not os.path.exists("./data/"+conf.file_clustered_data):
    #    print("./data/"+conf.file_clustered_data+" does not exist!")
    #else:
    #    print("loading clustered data from file to skip process of clustering: ./data/"+conf.file_clustered_data)
    #    data=pd.read_csv("./data/"+conf.file_clustered_data,encoding='utf-16',sep='\t')
    if not data.empty:
        data = pd.DataFrame(get_densities(data))
    else:
        print("DataFrame is Empty! cannot continue with density-wise clustering.")
    #
    #######################################
    # REMOVE NOISE DATA
    #######################################
    # INSTRUCTION: uncomment the below code line if you want to read from file to reduce time
    #if not os.path.exists("./data/"+conf.file_density_data):
    #    print("./data/"+conf.file_density_data+" does not exist!")
    #else:
    #    print("loading denisty data from file to skip process of denisty-wise clustering: ./data/"+conf.file_density_data)
    #    data=pd.read_csv("./data/"+conf.file_density_data,encoding='utf-16',sep='\t')
    if not data.empty:
        data = pd.DataFrame(drop_cliques_of_size(data, 1))
    else:
        print("DataFrame is Empty! cannot continue with removing noise data.")
    #
    #######################################
    # PLOT THE DATA
    #######################################
    # INSTRUCTION: uncomment the below code line only if you want to read from file to reduce time
    #if not os.path.exists("./data/"+conf.file_no_noise_data):
    #    print("./data/"+conf.file_no_noise_data+" does not exist!")
    #else:
    #    print("loading data without noise from file to skip process of removing noise: ./data/"+conf.file_no_noise_data)
    #    data = pd.read_csv("./data/"+conf.file_no_noise_data, encoding="utf-16",sep="\t")
    #
    if not data.empty:
        plot_all_clusters_before_after(data)
        plot_cluster_comparison_before_after(data)
        plot_reporting_delays(data)
        plot_nearest_neighbor_timeseries(data)
    else:
        print("DataFrame is Empty! cannot continue with plotting.")
else:
    print("DataFrame is Empty! no data retrieved; cannot continue repat!")
tfinish = dt.datetime.now()
print("ending Repat at "+str(tfinish)+" with a total time of "+str(tfinish - tstart))
#
