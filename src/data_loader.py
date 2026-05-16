"""Loads the historical international match results dataset from Kaggle.

The loader also annotates each match with two weights used downstream:
a tournament-importance weight and a recency weight, plus their product
as a single combined `sample_weight` for model training.
"""

import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter

from config import TOURNAMENT_WEIGHTS, DEFAULT_TOURNAMENT_WEIGHT


def get_recency_weight(date):
    """Return a recency weight in [0, 1] for a match date.

    The cutoffs are aligned with World Cup tournament start dates: matches
    played within the most recent cycle get full weight, while older
    matches decay in fixed steps. Matches before the 2010 cycle get
    weight 0 and are filtered out by `load_data`.

    Args:
        date: A pandas Timestamp representing the match date.

    Returns:
        A float weight: 1.0 (post-2022 WC), 0.7 (post-2018), 0.4
        (post-2014), 0.2 (post-2010), or 0.0 otherwise.
    """
    if date >= pd.Timestamp("2022-11-20"):
        return 1.0
    elif date >= pd.Timestamp("2018-06-14"):
        return 0.7
    elif date >= pd.Timestamp("2014-06-12"):
        return 0.4
    elif date >= pd.Timestamp("2010-06-11"):
        return 0.2
    else:
        return 0.0


def load_data():
    """Fetch the international match results dataset and prepare it for modelling.

    Pulls `results.csv` from the Kaggle dataset
    `martj42/international-football-results-from-1872-to-2017` via
    kagglehub, parses dates, attaches per-match `tournament_weight`,
    `recency_weight`, and combined `sample_weight` columns, drops
    matches that are either too old (recency weight 0) or unplayed
    (missing scores), and finally sorts chronologically.

    Returns:
        A pandas DataFrame of cleaned, weighted match rows sorted by
        date with a fresh range index.
    """
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "martj42/international-football-results-from-1872-to-2017",
        "results.csv",
    )

    # Parse dates up-front so downstream filtering / sorting works.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Map each match's tournament name to its importance weight; unknown
    # tournaments fall back to the default weight from config.
    df["tournament_weight"] = (
        df["tournament"].map(TOURNAMENT_WEIGHTS).fillna(DEFAULT_TOURNAMENT_WEIGHT)
    )

    # Combined sample weight = tournament importance x recency.
    df["recency_weight"] = df["date"].apply(get_recency_weight)
    df["sample_weight"] = df["tournament_weight"] * df["recency_weight"]

    df = df[df["recency_weight"] > 0] # only matches with relevant recency
    df = df.dropna(subset=["home_score", "away_score"]).copy() # drop unplayed matches

    # Chronological order is required for the Elo walk and rolling features.
    df = df.sort_values("date").reset_index(drop=True)

    return df