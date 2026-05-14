import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import pandas as pd

from src.data_loader import load_data
from src.elo import compute_elo
from src.features import concat_df, compute_features

def main():
    print("Loading data...")
    df = load_data()
    print(df.head())
    print(df.tail())
    print(df.shape)
    print(df["sample_weight"].isnull().sum())
    print(df["sample_weight"].describe())
    print(df["date"].min(), df["date"].max())

    print("\nComputing ELO ratings...")
    elo_df, elo_ratings = compute_elo(df)
    print(elo_df.shape)
    print(elo_df.head())
    print(sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)[:10])

    print("\nValidation checks...")
    print(df[df["home_score"].isna()].shape)
    print(elo_df[elo_df["elo_before"].isna()].shape)
    print(df.shape)

    print("\nFeatures DataFrame...")
    stats_df = concat_df(df)
    features_df = compute_features(elo_df, stats_df)
    print(features_df.shape)
    print(features_df.head())
    print(features_df.tail())
    print(features_df.isnull().sum())

    all_teams = pd.concat([df["home_team"], df["away_team"]]).unique()
    for team in all_teams:
        print(team)

    # null_teams = features_df[features_df["win_rate_10"].isnull()]["team"].unique()
    # print(null_teams)

if __name__ == "__main__":
    main()