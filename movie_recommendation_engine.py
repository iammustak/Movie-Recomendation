#!/usr/bin/env python
# coding: utf-8

# ### Simple Content-Based Movie Recommender

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Change path if needed
df = pd.read_csv("movie_dataset.csv")  # make sure this file is in the same folder

# We will use only these columns as "content" features
features = ["keywords", "cast", "genres", "director"]

# Fill NaN values with blank strings in the selected columns
for feature in features:
    df[feature] = df[feature].fillna("")

# Function to combine selected feature columns into a single string
def combine_features(row):
    # join all feature values as one string
    return " ".join([str(row[feature]) for feature in features])

# Create a new column with combined text features
df["combined_features"] = df.apply(combine_features, axis=1)

# Optionally check one row
# print(df.iloc[0]["combined_features"])

# Create the count matrix from the combined text
cv = CountVectorizer()
count_matrix = cv.fit_transform(df["combined_features"])

# Compute cosine similarity matrix
cosine_sim = cosine_similarity(count_matrix)

# Helper functions
def get_title_from_index(index: int) -> str:
    """Return movie title for a given DataFrame index."""
    return df.loc[index, "title"]  # using .loc because index is the actual DataFrame index


def get_index_from_title(title: str) -> int:
    """Return DataFrame index for a given movie title."""
    matches = df[df["title"] == title]
    if matches.empty:
        raise ValueError(f"Movie '{title}' not found in dataset.")
    return matches.index[0]  # return the actual DataFrame index


def get_similar_movies(movie_title: str):
    """Return list of (index, similarity_score) for movies similar to movie_title."""
    movie_index = get_index_from_title(movie_title)
    similar_movies = list(enumerate(cosine_sim[movie_index]))
    # sort by similarity (score at position 1 in tuple), highest first
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:]
    return sorted_similar_movies


def recommend_movies(movie_title: str, top_n: int = 5):
    """Print top N similar movies to the given movie title."""
    try:
        sorted_similar_movies = get_similar_movies(movie_title)
    except ValueError as e:
        print(e)
        return

    print(f"Top {top_n} similar movies to '{movie_title}' are:\n")
    count = 0
    for index, score in sorted_similar_movies:
        print(get_title_from_index(index))
        count += 1
        if count >= top_n:
            break


if __name__ == "__main__":
    # Example usage:
    # change the movie name as per your dataset
    # movie_user_likes = "Avatar"
    movie_user_likes = "Avatar"
    recommend_movies(movie_user_likes, top_n=5)
