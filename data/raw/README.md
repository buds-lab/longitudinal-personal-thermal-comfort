# enth-files-merging

Relevant python files: `Data-processing.py`, `formatting.py`, `Sensors_data.ipynb`, `User_data.ipynb`, `User_data.py`, `Create_folders.ipynb`, `Main.ipynb`, `Temp_humidity.ipynb`

Other files required: `awair_inventory.csv`, `Spaces-database.xlsx`

All these files should be in the `/data/raw/` folder

User data (individual): cozie, fitbit, yak, ibutton

Sensor data (for all users): ubibot, bms, awair, purpleair

Merged csv files can be found in the `merged-files` branch

## Procedure
1. Retrieve files from `/data/raw/` in `buds-lab` repo
2. Place all files from this repo and the other relevant files above into `/data/raw/`
3. Run `Create_folders.ipynb` to sort the files from `/data/raw/` into different folders
4. **There are some older files in `enth05` and `enth09` that should be removed manually.** There should only be 5 csv files for each user.
5. Run `Sensors_data.ipynb` to process and format all sensor datasets into new files
6. Run `Main.ipynb` to process every user data with the sensor data (this will take quite long, around 20 minutes to an hour)
7. Run `Temp_humidity.ipynb` to add columns for temp, light and humidity without being separated by the type of sensor
8. There will be csv files created for each user eg `enth01_merged_z.csv` and another file for all users `enth_all_users_merged.csv` & `enth_new_cols_z.csv`

## Info on files

###### `Data-processing.py`

Merges the data found on each users' individual devices according to the time of every cozie entry.

Contains functions to format the time to a standard format and calculate the average per minute for fitbit measurements. 

Used in `User_data.ipynb` and `User_data.py`.
 
###### `formatting.py`

Contains functions to 
1. format time to the standard format for sensor data 
2. format to upper snake case when comparing strings 
3. replace `NaN` `space_id` values with `-1`

*`NaN` values have to be replaced with `-1` to allow data to merge correctly using `merge_asof`

Used in `Sensors_data.ipynb` and `User_data.ipynb` and `User_data.py`

###### `Sensors_data.ipynb`

Processing the sensor data files and merging each dataset, and creates a csv file for each merged dataset.

###### `User_data.ipynb`

Only used as a visual guide. Step-by-step notebook on merging every dataset for an individual user using the files created in `Sensors_data.ipynb`

Relevant functions are included in `User_data.py` which are used in `Main.ipynb`.

###### `User_data.py`

Contains functions to merge every dataset with each individual as shown in `User_data.ipynb`.

Used in `Main.ipynb`.

###### `Main.ipynb`

Processes data and creates a new csv file for each user, as well as a file for all users' data combined.

Also changes each column name to be more readable.

###### `Temp_light_humidity.ipynb`

Adds in 3 columns for indoor temperature, light and humidity for each user without being separated by sensor. Data from ubibot sensor is prioritised.

###### `Create_folders.ipynb`

Renames user data files to include the corresponding devices and copies them to a new folder with users' names

Executed before processing any user data in `/data/raw/` directory.
