# Reads title.basics.tsv and outputs title.tsv
# Titles which are not of type "movie", "tvMovie", "short" or "tvShort" are removed.

import pandas as pd
import numpy as np

print("Loading data")
data = pd.read_csv("./title.basics.tsv", sep="\t", header=0)

print("Converting")

def find_movies(row):
    if row in ("movie", "tvMovie", "short", "tvShort"):
        return row
    return np.nan

def replace_missing(row):
    if row == "\\N":
        return np.nan
    return row

data["titleType"] = data["titleType"].apply(find_movies)
data["genres"] = data["genres"].apply(replace_missing)
data.dropna(subset=("titleType", "genres"), inplace=True)

data.drop(columns=["originalTitle", "isAdult", "startYear", "endYear", "runtimeMinutes"], inplace=True)

print("Saving")
data.to_csv("title.tsv", sep="\t")