# Calculates how many unique actors, and how many in total an actor has worked with
# Requires the principals.tsv file generated by the title_principals.py script
# Outputs the information to actor_relationships.tsv

import pandas as pd
import numpy as np

data = pd.read_csv("../data/principals.tsv", sep="\t", header=0)
data.drop(columns="Unnamed: 0", inplace=True)

grouped = data.groupby(["tconst"]).nconst.apply(lambda rows: ",".join(rows))

#grouped.to_csv("./grouped_actors.tsv", sep="\t", header=True)
#grouped = pd.read_csv("./grouped_actors.tsv", sep="\t", header=0, index_col=0).nconst

rels = {}

for _, nconsts in grouped.items():
    ns = nconsts.split(",")
    for n in ns:
        rels.setdefault(n, []).extend(ns)

for key in rels:
    rels[key] = [e for e in rels[key] if key != e]

df = pd.DataFrame()
keys = list(rels.keys())
df = df.reindex(labels=keys)
df["unique"] = pd.Series([len(set(rels[key])) for key in keys], index=df.index)
df["total"] = pd.Series([len(rels[key]) for key in keys], index=df.index)

df.to_csv("../data/actor_relationships.tsv", sep="\t", header=True)