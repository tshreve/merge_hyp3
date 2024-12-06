#!/usr/bin/env python

from collections import defaultdict
from utils_merge import extract_dates
import re
import os 

def search_intf(path,data_folder):
    """
    Search for interferogram matching dates in order to merge datasets

    Parameters:
    path (str) : data folder directory

    Returns:
    intf_dates_dict (dict) : dictionary of interferogram dates and corresponding folders

    """
    # Define root directory
    dates1 = []
    dates2 = []

    intf_dates = []

    # Loop through all folders in root directory
    for folder in path.glob(f'{data_folder}/*/'):

      dates = extract_dates(os.path.basename(folder))
      date1 = dates[0]
      date2 = dates[1]

    # Define date 1 and 2 based on file name
      #date1 = os.path.basename(folder)[5:13]
      #date2 = os.path.basename(folder)[21:29]
      intf_date = date1 + '_' + date2

    # If ref date not already in dates1, save folder
      if date1 not in dates1:
        dates1.append(date1)
        dates2.append(date2)
        intf_dates.append([intf_date,folder])

    # If secondary date not already in dates2, save folder
      elif date2 not in dates2:
        dates2.append(date2)
        intf_dates.append([intf_date,folder])

    # If interferogram date not already in intf_dates, save folder

      elif intf_date not in intf_dates:
        intf_dates.append([intf_date,folder])

    # If interferogram date already in intf_dates, intergerogram is to be merged
      else:
        intf_dates.append([intf_date,folder])

    # Allow dictionary to handle lists
    intf_dates_dict = defaultdict(list)

    # Create dictionary with lists of all folders to be merged
    for k, v in intf_dates:
        intf_dates_dict[k].append(v)

    return intf_dates_dict