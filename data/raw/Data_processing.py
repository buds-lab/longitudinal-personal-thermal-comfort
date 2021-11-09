"""
The functions here merge the data for each user individually
"""

import pandas as pd
import datetime as dt

def format_and_sort_time(file):
    """
    takes in a csv file name in string, returns a DataFrame
    standardises time format and sorts in chronological order
    date time format is year/month/date hour:minute timezone
    """
    if "ibutton_skin" in file:
        formatted = pd.read_csv(file, skiprows=19).rename(columns={"Date/Time" : "time", "Value" : "Skin Temp(℃)"})
        formatted = formatted.drop(columns="Unit")
    elif "ibutton_ambient" in file:
        formatted = pd.read_csv(file, skiprows=19).rename(columns={"Date/Time" : "time", "Value" : "Ambient Temp(℃)"})
        formatted = formatted.drop(columns="Unit")
        #skip the test description and standardise the "time" column for ibutton file
    else:
        formatted = pd.read_csv(file)
    formatted["time"] = pd.to_datetime(formatted["time"], errors="coerce").dt.strftime("%d/%m/%Y %H:%M +0800")
    formatted["time"] = pd.to_datetime(formatted["time"], format = "%d/%m/%Y %H:%M %z", errors="coerce") #to convert to datetime object
    return formatted.sort_values("time")

def fitbit_avg_per_min(file):
    """
    takes in a csv file name in string, returns a DataFrame
    only used for the fitbit files to get the average value per minute
    formats and sorts as above
    """
    formatted = format_and_sort_time(file)
    formatted = formatted.resample("T", on = "time").mean().reset_index().dropna()
    formatted["time"] = pd.to_datetime(formatted["time"]).dt.strftime("%d/%m/%Y %H:%M +0800")
    formatted["time"] = pd.to_datetime(formatted["time"], format = "%d/%m/%Y %H:%M %z")
    #to convert to datetime object so that they can be sorted not as a String
    return formatted.sort_values("time")

def cozie_intervals(file_names):
    """
    takes in a list of file names, returns a DataFrame with all files formatted and sorted
    values will correspond to cozie time intervals
    """
    cozie_file = list(filter(lambda x: "cozie" in x, file_names))
    other_files = list(filter(lambda x: "cozie" not in x, file_names))
    df = format_and_sort_time(cozie_file[0])
    for file in other_files:
        if "fitbit" in file:
            newfile = fitbit_avg_per_min(file)
            if newfile.empty:
                newfile["time"] = df["time"] #there is one user with no fitbit data at all, resulting in an empty dataframe
            df = pd.merge_asof(df, newfile, on = "time")
        else:
            newfile = format_and_sort_time(file)
            df = pd.merge_asof(df, newfile, on='time')
    return df.set_index("time")

#enth_names = {"Date/Time" : "time", "fitbit.air-vel" : "fitbit_air_vel", "fitbit.bodyPresence" : "fitbit_body_presence", "fitbit.change" : "fitbit_change", "fitbit.clothing": "fitbit_clothing", "fitbit.comfort" : "fitbit_comfort", "fitbit.heartRate" : "fitbit_heart_rate", "fitbit.indoorOutdoor" : "fitbit_indoor_outdoor", "fitbit.lat" : "fitbit_lat", "fitbit.lon" : "fitbit_lon", "fitbit.met" : "fitbit_met", "fitbit.responseSpeed" : "fitbit_response_speed", "fitbit.restingHR": "fitbit_resting_heart_rate", "fitbit.thermal" : "fitbit_thermal", "fitbit.voteLog" : "fitbit_vote_log", "fitbit_api.HR" : "fitbit_api_heart_rate", "fitbit_api.Steps" : "fitbit_api_steps", "Unit" : "ibutton_unit", "Value" : "ibutton_value"}
#standardise and rename the column names to lower_snake_case

#def ibutton_intervals(file_names):
#    """
#    takes in a list of all file names
#    returns a DataFrame with all files formatted and sorted
#    values will correspond to ibutton time intervals (10 min) with 2 hours tolerance
#    since not all of them match, there will be a lot of missing values
#    """
#    ibutton_files = list(filter(lambda x: "ibutton" in x, file_names))
#    merged_ibuttons = pd.merge_asof(format_and_sort_time(ibutton_files[0]), format_and_sort_time(ibutton_files[1]), on = "time")
#    df = merged_ibuttons #initial dataframe will have the ibutton data so that all other data correspond to their time intervals
#    files = filter(lambda x: "ibutton" not in x, file_names)
#    for file in files:
#        if "fitbit" in file:
#            newfile = fitbit_avg_per_min(file)
#            df = pd.merge_asof(df, newfile, on = "time")#, tolerance = pd.Timedelta("2 hours"))
#        else:
#            newfile = format_and_sort_time(file)
#            df = pd.merge_asof(df, newfile, on='time', tolerance = pd.Timedelta("2 hours"))
#    return df.rename(columns=new_col_names).set_index("time")
