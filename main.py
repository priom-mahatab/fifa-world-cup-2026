"""Entry point that wires together the full simulation pipeline.

Runs the stages in order: load historical match data, compute Elo ratings,
build rolling-form features, train the Poisson goals model, and then
simulate every group of the 2026 World Cup to determine the 32 teams
that advance to the knockout round.
"""

import sys
import os

# Make the local `src/` package importable without requiring installation.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import pandas as pd

from data_loader import load_data
from elo import compute_elo
from features import concat_df, compute_features
from model import train_model
from simulator import simulate_match, simulate_group, get_qualifiers
from config import GROUPS, WORLD_CUP_TEAMS

def main():
    """Run the end-to-end World Cup simulation pipeline.

    Loads the historical results, derives Elo ratings and rolling-form
    features for every team, trains the Poisson model, simulates each
    of the 12 groups, and prints the standings plus the list of teams
    that advance to the Round of 32.
    """
    # Stage 1: load and clean the raw Kaggle match results.
    # print("Loading data...")
    df = load_data()
    # print(df.head())
    # print(df.tail())
    # print(df.shape)
    # print(df["sample_weight"].isnull().sum())
    # print(df["sample_weight"].describe())
    # print(df["date"].min(), df["date"].max())

    # Stage 2: walk through matches in chronological order to build an
    # Elo history (one row per team per match) and the latest ratings.
    # print("\nComputing ELO ratings...")
    elo_df, elo_ratings = compute_elo(df)
    # print(elo_df.shape)
    # print(elo_df.head())
    # print(sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)[:10])

    # print("\nValidation checks...")
    # print(df[df["home_score"].isna()].shape)
    # print(elo_df[elo_df["elo_before"].isna()].shape)
    # print(df.shape)

    # Stage 3: stack home and away match rows into a single per-team
    # frame and compute rolling-window form features that the model
    # uses as predictors.
    # print("\nFeatures DataFrame...")
    stats_df = concat_df(df)
    features_df = compute_features(elo_df, stats_df)
    # print(features_df.shape)
    # print(features_df.head())
    # print(features_df.tail())
    # print(features_df.isnull().sum())

    all_teams = pd.concat([df["home_team"], df["away_team"]]).unique()
    # for team in all_teams:
    #     print(team)

    # null_teams = features_df[features_df["win_rate_10"].isnull()]["team"].unique()
    # print(null_teams)

    # Stage 4: fit the Poisson regressor that predicts a team's expected
    # goals (lambda) from its features. The scaler is returned so the
    # simulator can apply the same standardisation at predict time.
    model, scaler = train_model(features_df)
    # print(model.coef_)
    # print(model.intercept_)

    # print(simulate_match("Argentina", "France", model, scaler, features_df))
    # print(simulate_match("England", "Brazil", model, scaler, features_df))
    # print(simulate_match("Morocco", "Spain", model, scaler, features_df))

    all_group_teams = [team for group in GROUPS.values() for team in group]
    # for team in all_group_teams:
    #     if team in features_df["team"].values:
    #         print(f"{team}")

    # Stage 5: simulate every group, keeping the final standings keyed
    # by group letter so the qualification logic can rank third-placed
    # teams across groups afterwards.
    all_standings = {}
    for group_name, teams in GROUPS.items():
        standings = simulate_group(group_name, teams, model, scaler, features_df)
        all_standings[group_name] = standings
        print(f"\nGroup {group_name}")
        print(standings[["team", "played", "wins", "draws", "losses", "goals_for", "goals_against", "goal_difference", "points"]])

    # Stage 6: resolve the 32-team knockout bracket — group winners,
    # runners-up, and the 8 best third-placed teams.
    qualifiers = get_qualifiers(all_standings)
    print("Group Winners:", qualifiers["group_winners"])
    print("Runners Up:", qualifiers["group_runners_up"])
    print("Best 3rd:", qualifiers["best_third"])
    print("Total:", len(qualifiers["group_winners"]) + len(qualifiers["group_runners_up"]) + len(qualifiers["best_third"]))


if __name__ == "__main__":
    main()