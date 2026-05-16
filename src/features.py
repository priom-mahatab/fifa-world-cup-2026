"""Per-team rolling-form feature engineering.

Reshapes the wide match table (one row per match with home/away columns)
into a long, per-team view, then merges it with the Elo history and
derives 10- and 20-match rolling windows for win rate, average goals
scored, average goals conceded, and clean-sheet rate.
"""

import pandas as pd
import numpy as np

def concat_df(df):
    """Stack a wide match DataFrame into a long, per-team view.

    Each match contributes two rows: one from the home team's perspective
    and one from the away team's. Both rows expose `goals_scored` and
    `goals_conceded` columns relative to the team, so downstream
    aggregations don't have to special-case home vs away.

    Args:
        df: Match DataFrame with `home_team`, `away_team`, `home_score`,
            `away_score`, `date`, and `sample_weight` columns.

    Returns:
        A DataFrame with columns `date`, `team`, `goals_scored`,
        `goals_conceded`, and `sample_weight` — two rows per input match.
    """

    # Home perspective: home team's scored = home_score, conceded = away_score.
    home_stats = df[["date", "home_team", "home_score", "away_score", "sample_weight"]].copy()
    home_stats = home_stats.rename(columns={
        "home_team": "team",
        "home_score": "goals_scored",
        "away_score": "goals_conceded"
    })

    # Away perspective: away team's scored = away_score, conceded = home_score.
    away_stats = df[["date", "away_team", "away_score", "home_score", "sample_weight"]].copy()
    away_stats = away_stats.rename(columns={
        "away_team": "team",
        "away_score": "goals_scored",
        "home_score": "goals_conceded"
    })

    result = pd.concat([home_stats, away_stats], ignore_index=True)

    return result

def compute_features(elo_df, concatenated_df):
    """Build the per-team feature table used to train the goals model.

    Joins the Elo-per-match history with the long-form goal stats, then
    computes rolling 10- and 20-match windows for win rate, goals scored,
    goals conceded, and clean-sheet rate. Each rolling stat is shifted by
    one row so that the feature for a given match reflects only matches
    *before* it (avoiding target leakage).

    Args:
        elo_df: Output of `compute_elo` — one row per team per match
            with `team`, `date`, `elo_before`, `elo_after`, and
            `actual_result`.
        concatenated_df: Output of `concat_df` — long-format goals data.

    Returns:
        A DataFrame indexed by (team, date) ordering with all base
        columns plus the eight rolling-window features expected by
        the model (matches `config.FEATURE_COLS`).
    """
    # Pull goal stats onto the Elo rows so we can derive win and clean-sheet flags.
    df_merged = elo_df.merge(concatenated_df, on=["date", "team"], how="left")

    df_merged["is_win"] = np.where(df_merged["actual_result"] == 1.0, 1, 0)
    df_merged["is_clean_sheet"] = np.where(df_merged["goals_conceded"] == 0, 1, 0)
    # Sort within each team chronologically so rolling windows are valid.
    df_merged = df_merged.sort_values(["team", "date"]).reset_index(drop=True)

    # 10 match features — shift(1) excludes the current match from the window
    # so a row's feature is purely backward-looking (no target leakage).
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

    # Backfill missing rolling values: first the team's own mean (handles
    # early-career NaNs from shift+rolling), then the global mean as a
    # final safety net for teams with no history at all.
    for col in rolling_cols:
        df_merged[col] = df_merged.groupby("team")[col].transform(
            lambda x: x.fillna(x.mean())
        )
        df_merged[col] = df_merged[col].fillna(df_merged[col].mean())
        
    return df_merged

