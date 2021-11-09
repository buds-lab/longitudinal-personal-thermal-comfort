import os
import Data_processing as proc
import pandas as pd
import numpy as np
import formatting as fm

spaces_database = pd.read_csv("spaces_database_z.csv").drop(columns=["Unnamed: 0"])
sde1_spaces = spaces_database.loc[spaces_database["space_id"] >= 100].loc[spaces_database["space_id"] < 200]
sde1_corridors = sde1_spaces.loc[sde1_spaces["space_name"].str.contains("CORRIDOR", regex=False)]
sde1_corridors = list(sde1_corridors["space_id"])

def remap_locations(df):
    """
    classify space_id = 0 as outdoors
    change SDE1 corridors to outdoor except corridor_4_2 (space_id = 135)
    remap space_id 135 to 121
    """
    for row in range(len(df)):
        if df.at[row, "space_id"] == 0:
            df.at[row, "fitbit.indoorOutdoor"] = 9
        elif df.at[row, "space_id"] in sde1_corridors:
            if df.at[row, "space_id"] == 135:
                df.at[row, "space_id"] = 121
                df.at[row, "fitbit.indoorOutdoor"] = 11
            else:
                df.at[row, "fitbit.indoorOutdoor"] = 9
    return df

def merge_user_data(files):
    user_data = proc.cozie_intervals(files)\
    .rename(columns={"Steerpath.Space_id" : "space_id"})\
    .astype({"space_id" : "Int64"})\
    .reset_index()
    #rename to a standard "space_id" column so can merge easily
    user_data = fm.replace_nan_space_id(user_data)
    user_data = remap_locations(user_data)
    return user_data.set_index("time")

def merge_ubibot(stage0):
    ubibot = pd.read_csv("ubibot_dataset_z.csv")
    to_drop = ubibot.loc[ubibot["time"].isnull()] #this is the offending row with no time!!
    ubibot = ubibot.drop(to_drop.index[0])
    ubibot = fm.format_time(ubibot)
    ubibot = ubibot.astype({"space_id" : "Int64"}).sort_values("time")
    return pd.merge_asof(stage0, ubibot, on="time", by="space_id").set_index("time")

def format_bms(old_df):
    """
    removes bms data that is not required for the user ie locations not visited
    also adds in a column for faculty name to be used for merging with purpleair data
    """
    df = old_df.copy()
    df["faculty_name"] = ""
    for row in range(len(df)):
        space_id = df.at[row, "space_id"]
        if space_id >= 0:
            if space_id < 100:
                df.at[row, "faculty_name"] = "SDE4"
            elif space_id < 200:
                df.at[row, "faculty_name"] = "SDE1"
            else:
                df.at[row, "faculty_name"] = "SDE2"
        bms_cols = [col for col in df.columns if 'VAV' in col]
        for col in bms_cols:
            if space_id < 0:
                df.at[row, col] = np.nan
            elif str(space_id) == col[-3:]:
                continue
            else:
                df.at[row, col] = np.nan
    return df

def merge_bms(stage1):
    bms = fm.format_time(pd.read_csv("bms_dataset_z.csv")).sort_values("time")
    stage2 = format_bms(pd.merge_asof(stage1, bms, on="time")).set_index("time")
    return stage2

def merge_awair(stage2):
    awair = fm.format_time(pd.read_csv("awair_dataset_z.csv")).astype({"space_id" : "Int64"})
    awair = fm.replace_nan_space_id(awair).sort_values("time")
    stage3 = pd.merge_asof(stage2, awair, on="time", by="space_id").set_index("time")
    stage3.loc[(stage3["space_id"] == -1), stage3.columns[-9:]] = np.nan
    #since we treat nan space_id as -1, awair data where space_id is -1 will also show up in the user data, so we remove them
    return stage3

def merge_sensing(stage3):
    sensing = fm.format_time(pd.read_csv("sensing_dataset_z.csv")).astype({"space_id" : "Int64"})
    sensing = fm.replace_nan_space_id(sensing).sort_values("time")
    stage4 = pd.merge_asof(stage3, sensing, on="time", by="space_id").set_index("time")
    stage4.loc[(stage4["space_id"] == -1), stage4.columns[-4:]] = np.nan
    #since we treat nan space_id as -1, awair data where space_id is -1 will also show up in the user data, so we remove them
    return stage4

def merge_purpleair(stage4):
    purpleair = fm.format_time(pd.read_csv("purpleair_dataset_z.csv")).sort_values("time")
    stage5 = pd.merge_asof(stage4, purpleair, on="time", by="faculty_name").set_index("time")
    return stage5

def reorder_columns(stage5):
    cols = list(stage5.columns)
    cols.remove("space_id")
    cols.remove("faculty_name")
    new_cols = ["space_id"] + ["faculty_name"] + cols
    stage6 = stage5[new_cols] #reorder the columns so that space_id and faculty_name can be in front
    return stage6

def merge_all(files):
    """
    takes in a list of csv files for the user measurements
    """
    return reorder_columns(merge_purpleair(merge_sensing(merge_awair(merge_bms(merge_ubibot(merge_user_data(files)))))))