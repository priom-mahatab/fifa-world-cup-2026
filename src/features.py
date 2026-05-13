import pandas as pd
import numpy as np

def concat_df(df):

    home_stats = df[["date", "home_team", "home_score", "away_score"]].copy()
    home_stats = home_stats.rename(columns={
        "home_team": "team",
        "home_score": "goals_scored",
        "away_score": "goals_conceded"
    })

    away_stats = df[["date", "away_team", "away_score", "home_score"]].copy()
    away_stats = away_stats.rename(columns={
        "away_team": "team",
        "away_score": "goals_scored",
        "home_score": "goals_conceded"
    })

    result = pd.concat([home_stats, away_stats], ignore_index=True)

    return result

def compute_features(elo_df, concatenated_df):
    df_merged = elo_df.merge(concatenated_df, on=["date", "team"], how="left")

    df_merged["is_win"] = np.where(df_merged["actual_result"] == 1.0, 1, 0)
    df_merged["is_clean_sheet"] = np.where(df_merged["goals_conceded"] == 0, 1, 0)
    df_merged = df_merged.sort_values(["team", "date"]).reset_index(drop=True)

    # 10 match features
    df_merged["win_rate_10"] = df_merged.groupby("team")["is_win"].transform(
        lambda x: x.shift(1).rolling(10, min_periods=1).mean()
    )

    df_merged["avg_goals_scored_10"] = df_merged.groupby("team")["goals_scored"].transform(
        lambda x: x.shift(1).rolling(10, min_periods=1).mean()
    )

    df_merged["avg_goals_conceded_10"] = df_merged.groupby("team")["goals_conceded"].transform(
        lambda x: x.shift(1).rolling(10, min_periods=1).mean()
    )

    df_merged["clean_sheet_rate_10"] = df_merged.groupby("team")["is_clean_sheet"].transform(
        lambda x: x.shift(1).rolling(10, min_periods=1).mean()
    )

    # 20 match features
    df_merged["win_rate_20"] = df_merged.groupby("team")["is_win"].transform(
        lambda x: x.shift(1).rolling(20, min_periods=1).mean()
    )

    df_merged["avg_goals_scored_20"] = df_merged.groupby("team")["goals_scored"].transform(
        lambda x: x.shift(1).rolling(20, min_periods=1).mean()
    )

    df_merged["avg_goals_conceded_20"] = df_merged.groupby("team")["goals_conceded"].transform(
        lambda x: x.shift(1).rolling(20, min_periods=1).mean()
    )

    df_merged["clean_sheet_rate_20"] = df_merged.groupby("team")["is_clean_sheet"].transform(
        lambda x: x.shift(1).rolling(20, min_periods=1).mean()
    )

    rolling_cols = [
        "win_rate_10", "win_rate_20",
        "avg_goals_scored_10", "avg_goals_scored_20",
        "avg_goals_conceded_10", "avg_goals_conceded_20",
        "clean_sheet_rate_10", "clean_sheet_rate_20"
    ]

    for col in rolling_cols:
        df_merged[col] = df_merged.groupby("team")[col].transform(
            lambda x: x.fillna(x.mean())
        )
        df_merged[col] = df_merged[col].fillna(df_merged[col].mean())
        
    return df_merged

