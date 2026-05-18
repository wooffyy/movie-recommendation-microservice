from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os
from typing import Optional
 
app = FastAPI(
    title="Movie Recommendation ML Service",
    description="Content-Based Filtering menggunakan TF-IDF + Cosine Similarity - Pertemuan 11",
    version="1.0.0"
)

# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

cosine_sim = joblib.load(os.path.join(MODEL_DIR, "cosine_sim.pkl"))
title_to_idx = joblib.load(os.path.join(MODEL_DIR, "title_to_idx.pkl"))
movies_df = pd.read_csv(os.path.join(MODEL_DIR, "movies_metadata.csv"))
 
class PredictRequest(BaseModel):
    title: str
    top_n: Optional[int] = 5

class MovieResult(BaseModel):
    id: int
    title: str
    overview: str
    genres: str

class PredictResponse(BaseModel):
    input_title: str
    recommendations: list[MovieResult]
    total: int
    service: str = "python-ml-fastapi"

class BatchPredictRequest(BaseModel):
    titles: list[str]
    top_n: Optional[int] = 5

class BatchPredictResponse(BaseModel):
    results: list[PredictResponse]
    total_processed: int
    service: str = "python-ml-fastapi"

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model": "TF-IDF + Cosine Similarity",
        "dataset": "TMDB 5000",
        "total_movies": len(movies_df)
    }

@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    try:
        title_key = req.title.strip().lower()

        if title_key not in title_to_idx:
            raise HTTPException(
                status_code=404,
                detail=f"Movie '{req.title}' not found in dataset"
            )

        idx = title_to_idx[title_key]
        scores = list(enumerate(cosine_sim[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:req.top_n + 1]

        recommendations = []
        for movie_idx, _ in scores:
            row = movies_df.iloc[movie_idx]
            recommendations.append(MovieResult(
                id=int(row["id"]),
                title=str(row["title"]),
                overview=str(row["overview"]) if pd.notna(row["overview"]) else "",
                genres=str(row["genres_clean"]) if pd.notna(row["genres_clean"]) else ""
            ))

        return PredictResponse(
            input_title=req.title,
            recommendations=recommendations,
            total=len(recommendations)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-predict", response_model=BatchPredictResponse)
async def batch_predict(req: BatchPredictRequest):
    results = []
    for title in req.titles:
        try:
            title_key = title.strip().lower()
            if title_key not in title_to_idx:
                continue  

            idx    = title_to_idx[title_key]
            scores = list(enumerate(cosine_sim[idx]))
            scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:req.top_n + 1]

            recommendations = []
            for movie_idx, _ in scores:
                row = movies_df.iloc[movie_idx]
                recommendations.append(MovieResult(
                    id=int(row["id"]),
                    title=str(row["title"]),
                    overview=str(row["overview"]) if pd.notna(row["overview"]) else "",
                    genres=str(row["genres_clean"]) if pd.notna(row["genres_clean"]) else ""
                ))

            results.append(PredictResponse(
                input_title=title,
                recommendations=recommendations,
                total=len(recommendations)
            ))

        except Exception:
            continue 

    return BatchPredictResponse(
        results=results,
        total_processed=len(results)
    )