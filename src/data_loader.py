import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter

from config import TOURNAMENT_WEIGHTS, DEFAULT_TOURNAMENT_WEIGHT


def get_recency_weight(date):
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
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "martj42/international-football-results-from-1872-to-2017",
        "results.csv",
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["tournament_weight"] = (
        df["tournament"].map(TOURNAMENT_WEIGHTS).fillna(DEFAULT_TOURNAMENT_WEIGHT)
    )

    df["recency_weight"] = df["date"].apply(get_recency_weight)
    df["sample_weight"] = df["tournament_weight"] * df["recency_weight"]

    df = df[df["recency_weight"] > 0] # only matches with relevant recency
    df = df.dropna(subset=["home_score", "away_score"]).copy() # drop unplayed matches

    df = df.sort_values("date").reset_index(drop=True)

    return df