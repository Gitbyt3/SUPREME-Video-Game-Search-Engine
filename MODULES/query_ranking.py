# query_ranking.py

import numpy as np
import pandas as pd
import os
import sys
import lightgbm as lgb
from utils import sigmoid_scaling, max_min_scaling

model = None

def init(model_object=None, train_if_missing=True):
    """
    Initialize the LambdaMART model.
    Args:
        model_object: a pre-trained LightGBM model (Booster)
        train_if_missing: if True and model_object is None, train model from scores.csv
    """
    global model

    if model_object is not None:
        model = model_object
        return

    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../lambdamart_model.txt'))

    if os.path.exists(model_path):
        model = lgb.Booster(model_file=model_path)
        sys.stderr.write("LambdaMART model loaded from file.\n")
        sys.stderr.flush()
    elif train_if_missing:
        sys.stderr.write("No model found. Training LambdaMART model from scores.csv...\n")
        sys.stderr.flush()
        model = train_model()
        model.save_model(model_path)


def compute_features(query: dict, df: pd.DataFrame, useLTR = True) -> pd.DataFrame:
    df = df.copy()


    # Example dataframe with a release_date column
    # Convert the release_date column to datetime objects
    temp_df = pd.to_datetime(df['Release_Date'], errors='coerce')

    # Extract the year from the release_date column
    df['Release_Year'] = temp_df.dt.year.fillna(0)

    intent = query.get("Intent", {})
    rating_boost = "rating_boost" in intent
    recency_boost = "recency_boost" in intent
    popularity_boost = "player_boost" in intent

    df["popularity_signal"] = (df["Plays"].fillna(0) + df["Playing"].fillna(0)) if useLTR else max_min_scaling(df["Plays"].fillna(0) + df["Playing"].fillna(0))
    df["recency_signal"] = (df["Release_Year"]) if useLTR else max_min_scaling(df["Release_Year"].apply(lambda x: max(0, x - 2000)))

    # NEW: dummy rating signal if not already present
    df["rating_signal"] = (df["Rating"].fillna(0)) if useLTR else max_min_scaling(df["Rating"].fillna(0))
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

def execute(query_id: str, processed_query: dict, candidates: pd.DataFrame, useLTR = True) -> pd.DataFrame:
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
    df = compute_features(processed_query, candidates, useLTR)

    # Extract required features for LTR model
    feature_cols = [
        "BM25 Score", "SBERT Score", "rating_signal", "popularity_signal",
        "recency_signal", "genre_match", "platform_match"
    ]

    X = df[feature_cols].fillna(0)

    if not useLTR:
        df["Final Score"] = (
            df["BM25 Score"] * 0.7 + df["SBERT Score"] * 0.3
            + df["rating_signal"] * 0.2 + df["popularity_signal"] * 0.2
            + df["recency_signal"] * 0.2
        )
    else:
        # Score using LambdaMART
        df["Final Score"] = model.predict(X)

    # Sort and return
    return df.sort_values(by="Final Score", ascending=False).reset_index(drop=True)

def log_to_stderr(message):
    sys.stderr.write(message + '\n')
    sys.stderr.flush()

def train_model():
    from sklearn.model_selection import train_test_split
    from lightgbm import early_stopping, log_evaluation
    from ast import literal_eval
    from candidate_retrieval import execute as retrieve_candidates
    from query_processing import execute as process_query

    scores_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scores.csv'))
    df = pd.read_csv(scores_path)

    def try_literal_eval(x):
        try:
            return literal_eval(x)
        except Exception:
            return []

    df['Genres'] = df['Genres'].apply(lambda x: try_literal_eval(x) if pd.notnull(x) else [])
    df['Platforms'] = df['Platforms'].apply(lambda x: try_literal_eval(x) if pd.notnull(x) else [])

    feature_rows = []
    skipped = 0

    for _, row in df.iterrows():
        raw_query = row["Query"]
        game_id = row["ID"]

        processed = process_query(raw_query)
        candidates = retrieve_candidates(processed)

        # Find matching game in candidates
        match = candidates[candidates["ID"] == game_id]
        if match.empty:
            skipped += 1
            continue

        match_row = match.iloc[0]
        feature_row = {
            "Query": raw_query,
            "ID": game_id,
            "Score": row["Score"],
            "Genres": row["Genres"],
            "Platforms": row["Platforms"],
            "BM25 Score": match_row["BM25 Score"],
            "SBERT Score": match_row["SBERT Score"],
            "Plays": match_row.get("Plays", 0),
            "Playing": match_row.get("Playing", 0),
            "Rating": match_row.get("Rating", 0),
            "Release_Date": match_row.get("Release_Date", "TBD")
        }
        feature_rows.append(feature_row)

    if skipped:
        sys.stderr.write(f"Skipped {skipped} queries due to missing ID in candidates.\n")
        sys.stderr.flush()

    features_df = pd.DataFrame(feature_rows)

    features_df['Genres'] = features_df['Genres'].apply(lambda x: x if isinstance(x, list) else [])
    features_df['Platforms'] = features_df['Platforms'].apply(lambda x: x if isinstance(x, list) else [])

    # Simulate query object per row
    feature_rows_full = []
    for _, row in features_df.iterrows():
        query = {"Genres": row["Genres"], "Platforms": row["Platforms"], "Intent": {}}
        row_df = pd.DataFrame([row])
        row_features = compute_features(query, row_df, useLTR=False)
        feature_rows_full.append(row_features)

    features_df = pd.concat(feature_rows_full, ignore_index=True)

    features = [
        "BM25 Score", "SBERT Score", "rating_signal",
        "popularity_signal", "recency_signal", "genre_match", "platform_match"
    ]
    required_cols = features + ['Query', 'Score']
    missing_cols = [col for col in required_cols if col not in features_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Cap to 200 per query
    features_df = features_df.groupby("Query", group_keys=False).apply(lambda g: g.head(200)).reset_index(drop=True)

    # Grouping by query
    features_df["group_id"] = features_df["Query"].astype("category").cat.codes
    train_ids, test_ids = train_test_split(features_df["group_id"].unique(), test_size=0.2, random_state=42)
    train_mask = features_df["group_id"].isin(train_ids)
    test_mask = features_df["group_id"].isin(test_ids)

    X_train = features_df.loc[train_mask, features]
    y_train = features_df.loc[train_mask, "Score"]
    group_train = features_df[train_mask].groupby("group_id").size().tolist()

    X_test = features_df.loc[test_mask, features]
    y_test = features_df.loc[test_mask, "Score"]
    group_test = features_df[test_mask].groupby("group_id").size().tolist()

    train_data = lgb.Dataset(X_train, label=y_train, group=group_train)
    test_data = lgb.Dataset(X_test, label=y_test, group=group_test, reference=train_data)

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [10],
        "learning_rate": 0.1,
        "num_leaves": 31,
        "min_data_in_leaf": 20,
        "verbose": -1
    }

    model = lgb.train(
        params,
        train_data,
        valid_sets=[train_data, test_data],
        valid_names=["train", "test"],
        num_boost_round=100,
        callbacks=[
            early_stopping(stopping_rounds=10),
            log_evaluation(period=10, logger=log_to_stderr)  # ← logs now go to stderr!
        ]
    )

    return model


