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
import matplotlib.pyplot as plt
from matplotlib import style
#from IPython.core.application import base_aliases pylab inline
style.use('ggplot')
from shapely.geometry import Polygon
import numpy as np
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
    y_list = df_plot[axis_list[0]].values
    x_list = df_plot[axis_list[1]].values
    # set color
    if 'Color' in df_plot:
        color_scheme = df_plot.Color
    #temp_color=rcolor(1)[0]
    plt.close('all')
    plt.scatter(x_list,y_list,s=300,linewidths=2)
    plt.title(title, color='grey', fontsize=14, fontweight='bold')
    plt.xlabel(axis_list[1],color='grey', fontsize=14)
    plt.ylabel(axis_list[0],color='grey', fontsize=14)
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    #
    return 0
#
# Define function to plot the data points on a map
#
def map_points(df_map,coord_list=['lat','lon'], titile = "map plot", fname="plot_map_points.png"):
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
    #plot borders of Nepal along with extracted points
    plt.close('all')
    plt.plot(map_lon,map_lat)
    plt.scatter(lon_points,lat_points,s=30,linewidths=2)
    plt.title(titile, color='grey', fontsize=14, fontweight='bold')
    plt.xlabel(coord_list[1],color='grey', fontsize=14)
    plt.ylabel(coord_list[0],color='grey', fontsize=14)
    plt.savefig("./plots/"+fname, dpi=300, bbox_inces='tight')
    #
    return 0