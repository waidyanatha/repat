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
#
# Define a function to remove all symbol characters and replace with a space 
def catesian(df_plot, axis_list=['x','y']):
    print axis_list
    
    return 0