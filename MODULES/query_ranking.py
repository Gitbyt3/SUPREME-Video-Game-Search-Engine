# query_ranking.py

import numpy as np
import pandas as pd

model = None

def init(model_object):
    """
    Initialize the LambdaMART model.
    Args:
        model_object: a pre-trained LightGBM model (Booster)
    """
    global model
    model = model_object


def compute_features(query: dict, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    intent = query.get("Intent", {})
    rating_boost = "rating_boost" in intent
    recency_boost = "recency_boost" in intent
    popularity_boost = "player_boost" in intent

    df["popularity_signal"] = df["Plays"] + df["Playing"]
    df["recency_signal"] = df["Release_Year"]

    # NEW: dummy rating signal if not already present
    df["rating_signal"] = df["Rating"].fillna(0)
    if rating_boost:
        df["rating_signal"] *= 1.5

    df["genre_match"] = df["Genres"].apply(
        lambda g: int(bool(set(g) & set(query.get("Genres", []))))
    )
    df["platform_match"] = df["Platforms"].apply(
        lambda p: int(bool(set(p) & set(query.get("Platforms", []))))
    )

    if popularity_boost:
        df["popularity_signal"] *= 1.5
    if recency_boost:
        df["recency_signal"] *= 1.5

    return df

def execute(query_id: str, processed_query: dict, candidates: pd.DataFrame) -> pd.DataFrame:
    """
    Apply LambdaMART model to re-rank candidates based on query intent and features.
    Args:
        query_id (str): ID of the current query
        processed_query (dict): Output from query_processing.execute()
        candidates (pd.DataFrame): Output from candidate_retrieval.execute()
    Returns:
        Re-ranked DataFrame with added 'Final Score'
    """
    if model is None:
        raise RuntimeError("You must call query_ranking.init() with a trained model first.")

    # Build feature set
    df = compute_features(processed_query, candidates)

    # Extract required features for LTR model
    feature_cols = [
        "BM25 Score", "SBERT Score", "rating_signal", "popularity_signal",
        "recency_signal", "genre_match", "platform_match"
    ]

    X = df[feature_cols].fillna(0)

    # Score using LambdaMART
    df["Final Score"] = model.predict(X)

    # Sort and return
    return df.sort_values(by="Final Score", ascending=False).reset_index(drop=True)