"""
contains functions to format the different measurements
"""

import pandas as pd
import datetime as dt

def format_time(df):
    """
    takes in a dataframe and formats the time
    this function differs from that in Data_processing.py in that it formats a dataframe, not a csv file
    """
    df["time"] = pd.to_datetime(df["time"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M +0800")
    df["time"] = pd.to_datetime(df["time"], format = "%d/%m/%Y %H:%M %z", errors="coerce") #to convert to datetime object
    return df

def reformat(string):
    """
    converts spaces to underscores and all upper case
    """
    new_string = ""
    for i in range(len(string)):
        if string[i] == " ":
            new_string += "_"
        else:
            new_string += string[i]
    return new_string.upper()

def replace_nan_space_id(df):
    """
    replaces nan space_id with -1
    """
    df["space_id"] = df["space_id"].fillna(-1)
    return df