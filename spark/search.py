import sys
import os
import ast
import pwd

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, udf
import pyspark.sql.types as sqltypes

worker_module_path = "/home/ubuntu/.local/lib/python3.5/site-packages/"

sim_model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
#sim_model = hub.load(sim_model_url)

# Read input from environment variables.
search_genres = os.environ["search_genres"].split(",")
num_search_genres = len(search_genres)
search_actors = [[descr.split(" ")[0], *descr.split(" ")[1].split("-")] for descr in os.environ["search_actors"].split(",")]
for a in search_actors:
    if len(a) == 2:
        a.append(a[1])
search_plot = os.environ["search_plot"]

# Connect to spark.
spark = SparkSession.builder.appName("PySpark Search").getOrCreate()

# Read actors froms file to DataFrame, and calculate their age.
actors = spark.read.csv("project/spark/actors.tsv/part*", header=True, sep="\t")
actors = actors.withColumn("age", expr("2020 - birthYear"))

# Read movies from file to DataFrame.
movies = spark.read.csv("project/spark/movies.tsv/part*", header=True, sep="\t")

# Create views to enable SQL statements.
actors.createOrReplaceTempView("Actors")
movies.createOrReplaceTempView("Movies")

# Decorator indicating that calc_average_score is an user-defined-function returning a float value.
@udf("float")
def calc_average_score(genre_score):
    score = 0
    genre_score = ast.literal_eval(genre_score)
    for genre in search_genres:
        score += genre_score.get(genre, -1000)
    return score / num_search_genres


def similarity_score():
    def executor(iterator):
        #import pkg_resources
        import sys
        if worker_module_path not in sys.path:
            sys.path.append(worker_module_path)

        #import tensorflow_hub as hub
        import numpy as np

        #sim_model = hub.load(sim_model_url)
        for row in iterator:
            for d in pkg_resources.working_set:
                yield str(d)
                #yield d.project_name + " " + d.version
            #sim = sim_model([search_plot, row.summary])
            #yield str(np.dot(sim[0], sim[1]))
    return executor

movie_sql = "SELECT tconst, summary as score from Movies WHERE summary != 'N/A'"
candidate_sql = "SELECT nconst, genre_score FROM Actors WHERE age >= {0} AND age <= {1} AND gender= {2}"

woho = spark.sql(movie_sql).rdd.mapPartitions(similarity_score())
print(set(woho.collect()))

#woho.toDF().write.csv("project/spark/simscore.tsv", sep="\t", header=True)

spark.stop()
"""
candidates = []
for i, desc in enumerate(search_actors):
    # Select actors based on the actor description
    cand = spark.sql(candidate_sql.format(desc[1], desc[2], 1 if desc[0] == "Female" else 0))

    # Create condition that will only select actors with all of the genres.
    genre_condition = cand.genre_score.contains(search_genres[0])
    if len(search_genres) > 1:
        for genre in search_genres[1:]:
            genre_condition &= cand.genre_score.contains(genre)

    cand = cand \
    # Get candidates with all genres
        .filter(genre_condition) \
    # Select the nconst column, and calculate the average genre score
        .select("nconst", calc_average_score("genre_score").alias("score")) \
    # Sort them by score in decreasing order
        .orderBy(["score"], ascending=False)
    candidates.append(cand)

    # Save candidates to disk
    cand.write.csv("project/spark/candidates{}.tsv/".format(i), sep="\t", header=True)

# Disconnect from spark
spark.stop()"""