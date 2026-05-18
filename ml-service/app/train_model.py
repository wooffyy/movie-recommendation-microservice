import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import ast
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# Load dataset (sumber: https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
movies  = pd.read_csv(os.path.join(DATASET_DIR, "tmdb_5000_movies.csv"))
credits = pd.read_csv(os.path.join(DATASET_DIR, "tmdb_5000_credits.csv"))

# Merge dataset movies & credits
credits.rename(columns={"movie_id": "id"}, inplace=True)
df = movies.merge(credits, on="id")
df = df[["id", "title_x", "overview", "genres", "keywords", "cast", "crew"]].copy()
df.rename(columns={"title_x": "title"}, inplace=True)

# Helper function buat parsing json string ke kolom
def parse_names(json_str, key="name", limit=None):
    try:
        items = ast.literal_eval(json_str)
        names = [i[key] for i in items]
        return " ".join(names[:limit] if limit else names)
    except:
        return ""

def get_director(crew_str):
    try:
        crew = ast.literal_eval(crew_str)
        for c in crew:
            if c["job"] == "Director":
                return c["name"].replace(" ", "")
        return ""
    except:
        return ""

# data preprocessing
df["genres_clean"] = df["genres"].apply(lambda x: parse_names(x))
df["keywords_clean"] = df["keywords"].apply(lambda x: parse_names(x))
df["cast_clean"] = df["cast"].apply(lambda x: parse_names(x, limit=3))
df["director"] = df["crew"].apply(get_director)
df["overview"] = df["overview"].fillna("")

# buat satu kolom "soup" biar tf-idf bisa vectorized sekaligus
df["soup"] = (
    df["overview"] + " " +
    df["genres_clean"] + " " +
    df["keywords_clean"] + " " +
    df["cast_clean"] + " " +
    df["director"]
)

df = df.dropna(subset=["soup"]).reset_index(drop=True)

# TF-IDF vectorizer
tfidf = TfidfVectorizer(stop_words="english", max_features=10000)
tfidf_matrix = tfidf.fit_transform(df["soup"])

print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

# Cosine Similarity Matrix 
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
print(f"Cosine similarity matrix shape: {cosine_sim.shape}")

# Mapping title ke index 
title_to_idx = pd.Series(df.index, index=df["title"].str.lower()).drop_duplicates()

# test 
def recommend(title, top_n=5):
    title = title.lower()
    if title not in title_to_idx:
        return f"Movie '{title}' not found"
    idx = title_to_idx[title]
    scores = list(enumerate(cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    return [df["title"].iloc[i] for i, _ in scores]

print("\nTest recommendation for 'The Dark Knight':")
print(recommend("The Dark Knight"))

# simpan model
MODEL_DIR = os.path.join(BASE_DIR, "app", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(tfidf, os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
joblib.dump(cosine_sim, os.path.join(MODEL_DIR, "cosine_sim.pkl"))
joblib.dump(title_to_idx, os.path.join(MODEL_DIR, "title_to_idx.pkl"))

df[["id", "title", "overview", "genres_clean"]].to_csv(
    os.path.join(MODEL_DIR, "movies_metadata.csv"), index=False
)

print("\nModel saved successfully")