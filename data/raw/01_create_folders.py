import os
import shutil

"""
creates folder from enth01 to enth29
"""
for i in range(1, 30):
    try:
        os.mkdir(f"enth{str(i).zfill(2)}")
    except FileExistsError:
        pass

"""
accesses every folder in this raw folder and checks if there is a enthxx.csv file
if there is, rename it to include the device because many files have the same name
eg enth01.csv --> enth01_yak.csv
"""
for folder in os.listdir():
    try:
        dire = f"{os.getcwd()}/{folder}"
        for file in os.listdir(folder):
            if "enth" in file and folder not in file and "csv" in file:
                source = f"{dire}/{file}"
                dest = f"{dire}/{file[:-4]}_{folder}.csv"
                os.rename(source, dest)
    except NotADirectoryError:
        continue

"""
copy the files to the respective user folders created above
"""
for folder in os.listdir():
    try:
        dire = f"{os.getcwd()}/{folder}"
        for file in os.listdir(folder):
            if "enth" in file and "csv" in file:
                try:
                    source2 = f"{dire}/{file}"
                    dest2 = f"{os.getcwd()}/{file[:6]}/{file}"
                    shutil.copy(source2, dest2)
                except shutil.SameFileError:
                    continue
    except NotADirectoryError:
        continue

"""
removes empty folders
"""
for folder in os.listdir():
    try:
        os.rmdir(folder)
    except OSError:
        continue

#removes folders without a cozie file
for folder in os.listdir():
    if "enth" in folder and "csv" not in folder:
        cozie_file = list(filter(lambda x: "cozie" in x, os.listdir(folder)))
        if not cozie_file:
            shutil.rmtree(folder)
