# Calculate genre scores for every actor based on the movies they have acted in.
# The score is the average user score.

import pandas as pd
import numpy as np

actors = pd.read_csv("../data/name.tsv", sep="\t", header=0, index_col=0)
titles = pd.read_csv("../data/title.tsv", sep="\t", header=0, index_col=0)
ratings = pd.read_csv("../data/ratings.tsv", sep="\t", header=0, index_col=0)

row_i = 0

def calculate_genre_score(row):
    global row_i
    row_i += 1
    if row_i % 100 == 0:
        print(row_i)

    # Actor is known for
    find_titles = row.knownForTitles.split(",")
    # Should we use principals.tsv instead to get more movies?
    # Get titles
    knownfor = titles.loc[titles.index.isin(find_titles)]["genres"]

    genre_scores = {}
    for tconst, gs in knownfor.items():
        if not tconst in ratings.index:
            # If they have acted in something that isn't published yet,
            # then the title with id tconst will not have a rating.
            continue

        r = ratings.loc[tconst].averageRating
        gs = gs.split(",")
        for g in gs:
            genre_scores.setdefault(g, []).append(r)

    for g in genre_scores:
        genre_scores[g] = np.mean(genre_scores[g])

    return genre_scores

print(actors.shape)
actors["genre_score"] = actors.apply(calculate_genre_score, axis=1)

scores = actors["genre_score"]
scores.to_csv("../data/genre_scores.tsv", sep="\t", header=True)