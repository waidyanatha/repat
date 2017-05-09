# REPAT - PLOT (plot data) 
#
# Instructions: 
#     - import (include) this library in main
#
# Reporting Patterns (RePat) for determining telecom availability during crises
# ------------------------------------------------------------------------------
#
# purpose of this code is to plot the clustered and other generated data for
# visualization in various forms
#
# contributors: nuwan@lirneasia.net and ilihdian@gmail.com
#
# ------------------------------------------------------------------
#
# import libraries
import sys, os, csv
import pyquery
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.cm as cm
#import matplotlib as mpl
from pandas.core.series import Series
from __builtin__ import str
#from IPython.core.application import base_aliases pylab inline
style.use('ggplot')
from shapely.geometry import Polygon
#
# Define a function to remove all symbol characters and replace with a space 
def catesian_plane(df_plot, axis_list=['x','y'], title = "cartesian plot", fname="plot_cartesian_plane.png"):
    y_list = df_plot[axis_list[0]].values
    x_list = df_plot[axis_list[1]].values
    #temp_color=rcolor(1)[0]
    plt.close('all')
    plt.plot(x_list,y_list,marker='o',markerfacecolor="green",markersize=10)
    #plt.scatter(x_list,y_list,marker='o',color="green",size=10)
    #plt.suptitle("Cartesian of "+axis_list[0]+" vs. "+axis_list[1], color='darkgrey')
    plt.title(title, color='grey', fontsize=18, fontweight='bold')
    plt.xlabel(axis_list[1],color='grey', fontsize=14)
    plt.ylabel(axis_list[0],color='grey', fontsize=14)
    #plt.ylim((0,3))
    #plt.yticks([1,2,3])
    
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    return 0
#
# Define a function to remove all symbol characters and replace with a space 
def scatter_plane(df_plot, axis_list=['x','y'], title = "Scatter Plot", fname="plot_scatter_plane.png"):
    #
    unique_plots = pd.DataFrame(df_plot['K_means'].unique())
    colors = cm.rainbow(np.linspace(0, 1, len(unique_plots)))
    #
    # setup the plot
    plt.close('all')
    fig, ax = plt.subplots(1,1, figsize=(8,8))
    # setup legend labels
    legend_labels = pd.DataFrame(columns=["Labels"])
    # plot all the points color coded by delay clusters
    for plot_index, plot_rows in unique_plots.iterrows():
        y_list = df_plot[axis_list[1]].loc[df_plot['K_means'] == plot_rows[0]]
        x_list = df_plot[axis_list[0]].loc[df_plot['K_means'] == plot_rows[0]]
        leg_min = ("%.2f" % y_list.min())
        leg_max = ("%.2f" % y_list.max())
        index_value = len(legend_labels)
        legend_labels.set_value(index_value, 'Labels', "Delay "+str(leg_min)+" to "+str(leg_max))
        scat = ax.scatter(x_list,y_list,color=colors[index_value],s=300,linewidths=1)
    #
    # add titile, labels, and axis names
    ax.set_title(title, color='grey', fontsize=14, fontweight='bold')
    ax.set_xlabel(axis_list[0],color='grey', fontsize=14)
    ax.set_ylabel(axis_list[1],color='grey', fontsize=14)
#    legend_labels = df_plot['K_means'].unique()
    legend_labels = legend_labels['Labels'].unique()
    ax.legend(legend_labels, loc='best')
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    #
    return fig
#
# Define a function to remove all symbol characters and replace with a space 
def scatter_map(df_map,coord_list=['lon','lat'], title = "map plot", fname="plot_map_scatter_points.png"):
    #
    base_map=pd.read_csv('./data/NP_L0.csv')
    stri=base_map.WKT[0]
    #parsing
    m = stri.split('((', 1)[1].split('))')[0]
    m = m.split(',')
    m = [list(map(float,item.split(' '))) for item in m]
    #
    #construct a polygon and extract coordinates
    poly_map=Polygon(m)
    map_lon=[item[0] for item in m]
    map_lat=[item[1] for item in m]
    #
    unique_plots = pd.DataFrame(df_map['K_means'].unique())
    colors = cm.rainbow(np.linspace(0, 1, len(unique_plots)+1))
    # setup legend labels
    legend_labels = pd.DataFrame(columns=["Labels"])
    #
    # setup the plot
    plt.close('all')
    fig, ax = plt.subplots(1,1, figsize=(8,8))
    ax.plot(map_lon,map_lat)
    legend_labels.set_value(0, 'Labels', "Map boundry")
    # plot all the points color coded by delay clusters
    for plot_index, plot_rows in unique_plots.iterrows():
        y_list = df_map[coord_list[1]].loc[df_map['K_means'] == plot_rows[0]]
        x_list = df_map[coord_list[0]].loc[df_map['K_means'] == plot_rows[0]]
        leg_min = ("%.2f" % df_map['Delay'].loc[df_map['K_means'] == plot_rows[0]].min())
        leg_max = ("%.2f" % df_map['Delay'].loc[df_map['K_means'] == plot_rows[0]].max())
        index_value = len(legend_labels)
        legend_labels.set_value(index_value, 'Labels', "Delay "+str(leg_min)+" to "+str(leg_max))
        scat = ax.scatter(x_list,y_list,color=colors[index_value],s=300,linewidths=1)
    #
    # add titile, labels, and axis names
    ax.set_title(title, color='grey', fontsize=14, fontweight='bold')
    ax.set_xlabel(coord_list[0],color='grey', fontsize=14)
    ax.set_ylabel(coord_list[1],color='grey', fontsize=14)
#    legend_labels = df_plot['K_means'].unique()
    legend_labels = legend_labels['Labels'].unique()
    ax.legend(legend_labels, loc='best')
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    #
    return fig
#
# Define function to plot the data points on a map
#
def map_points(df_map,coord_list=['lat','lon'], title = "map plot", fname="plot_map_points.png"):
    base_map=pd.read_csv('./data/NP_L0.csv')
    stri=base_map.WKT[0]
    #parsing
    m = stri.split('((', 1)[1].split('))')[0]
    m = m.split(',')
    m = [list(map(float,item.split(' '))) for item in m]
    #
    #construct a polygon and extract coordinates
    poly_map=Polygon(m)
    map_lon=[item[0] for item in m]
    map_lat=[item[1] for item in m]
    #
    lat_points = df_map[coord_list[0]].values
    lon_points = df_map[coord_list[1]].values
    color = df_map['Density']
    #plot borders of Nepal along with extracted points
    plt.close('all')
    plt.plot(map_lon,map_lat)
    # plot the clusters
    # add soe color
    plt.scatter(lon_points,lat_points,c=color,s=30,linewidths=2)
    plt.title(title, color='grey', fontsize=14, fontweight='bold')
    plt.xlabel(coord_list[1],color='grey', fontsize=14)
    plt.ylabel(coord_list[0],color='grey', fontsize=14)
    plt.legend(loc='best')
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    #
    return 0
#
# Define function to plot a time series of the data
#
def time_series_points(ts_df,ts_axis_list=['y','time'], title = "Time Series", fname="plot_ts_clusters.png"):
    #
    plt.figure()
    ts_df['Series'] = Series(list(range(len(ts_df))))
    ts_df.cumsum()
    #ts_df.plot(x='Series',y='Density')
    y_list = ts_df['Density'].values
    x_list = ts_df['Date'].values
    
    plt.scatter(x_list,y_list,s=300,linewidths=2)
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    #
    return 0

# #
# # Define function to plot the data points on a map
# #
# def map_before_after(df_map,coord_list=['lat','lon'], titile = "map plot", fname="plot_map_points.png"):
#     base_map=pd.read_csv('./data/NP_L0.csv')
#     stri=base_map.WKT[0]
#     #parsing
#     m = stri.split('((', 1)[1].split('))')[0]
#     m = m.split(',')
#     m = [list(map(float,item.split(' '))) for item in m]
#     #
#     #construct a polygon and extract coordinates
#     poly_map=Polygon(m)
#     map_lon=[item[0] for item in m]
#     map_lat=[item[1] for item in m]
#     #
#     lat_points = df_map[coord_list[0]].values
#     lon_points = df_map[coord_list[1]].values
#     #plot borders of Nepal along with extracted points
#     if 'Color' in df_plot:
#         color_scheme = df_plot.Color
# 
#     plt.close('all')
#     plt.plot(map_lon,map_lat)
#     plt.scatter(lon_points,lat_points,s=30,linewidths=2)
#     plt.title(titile, color='grey', fontsize=14, fontweight='bold')
#     plt.xlabel(coord_list[1],color='grey', fontsize=14)
#     plt.ylabel(coord_list[0],color='grey', fontsize=14)
#     plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
#     #
#     return 0