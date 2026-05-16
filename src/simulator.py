import pandas as pd
import numpy as np
from config import FEATURE_COLS
from itertools import combinations

def simulate_match(team_a, team_b, model, scaler, features_df):
    mrf_a = features_df[features_df["team"] == team_a].sort_values("date", ascending=False).iloc[0]
    mrf_b = features_df[features_df["team"] == team_b].sort_values("date", ascending=False).iloc[0]

    team_a_features = mrf_a[FEATURE_COLS]
    team_b_features = mrf_b[FEATURE_COLS]

    team_a_scaled = scaler.transform(pd.DataFrame([team_a_features], columns=FEATURE_COLS))
    team_b_scaled = scaler.transform(pd.DataFrame([team_b_features], columns=FEATURE_COLS))

    lambda_a = model.predict(team_a_scaled)[0]
    lambda_b = model.predict(team_b_scaled)[0]

    # Poisson sampling
    goals_a = np.random.poisson(lambda_a)
    goals_b = np.random.poisson(lambda_b)

    return goals_a, goals_b

def simulate_group(group_name, teams, model, scaler, features_df):
    group_df = pd.DataFrame({
        "team": teams,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0
    })
    matches = combinations(teams, 2)
    for match in matches:
        team_a = match[0]
        team_b = match[1]
        goals_a, goals_b = simulate_match(team_a, team_b, model, scaler, features_df)
        group_df.loc[group_df["team"] == team_a, "played"] += 1
        group_df.loc[group_df["team"] == team_b, "played"] += 1
        group_df.loc[group_df["team"] == team_a, "goals_for"] += goals_a
        group_df.loc[group_df["team"] == team_b, "goals_for"] += goals_b

        group_df.loc[group_df["team"] == team_a, "goals_against"] += goals_b
        group_df.loc[group_df["team"] == team_b, "goals_against"] += goals_a

        group_df.loc[group_df["team"] == team_a, "goal_difference"] += goals_a - goals_b
        group_df.loc[group_df["team"] == team_b, "goal_difference"] += goals_b - goals_a
        
        if goals_a > goals_b:
            group_df.loc[group_df["team"] == team_a, "wins"] += 1
            group_df.loc[group_df["team"] == team_a, "points"] += 3
            group_df.loc[group_df["team"] == team_b, "losses"] += 1

        elif goals_b > goals_a:
            group_df.loc[group_df["team"] == team_b, "wins"] += 1
            group_df.loc[group_df["team"] == team_b, "points"] += 3
            group_df.loc[group_df["team"] == team_a, "losses"] += 1
        
        else:
            group_df.loc[group_df["team"] == team_a, "draws"] += 1
            group_df.loc[group_df["team"] == team_a, "points"] += 1

            group_df.loc[group_df["team"] == team_b, "draws"] += 1
            group_df.loc[group_df["team"] == team_b, "points"] += 1
        
    group_df = group_df.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False
    ).reset_index(drop=True)

    return group_df



