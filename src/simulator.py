"""Tournament simulation: match, group stage, and qualification logic.

The match simulator pulls each team's most-recent feature row, feeds it
through the trained Poisson model to get expected goals (`lambda`), and
samples a final score from independent Poisson distributions. The group
and qualification helpers compose those match simulations into a full
group stage and resolve the 32-team knockout field.
"""

import pandas as pd
import numpy as np
from config import FEATURE_COLS
from itertools import combinations

def simulate_match(team_a, team_b, model, scaler, features_df):
    """Simulate a single match between two teams.

    Looks up the most recent feature snapshot for each team, scales the
    inputs with the training-time `scaler`, predicts each side's
    expected goals via the Poisson `model`, and draws an independent
    Poisson sample from each rate.

    Args:
        team_a: Name of the first team.
        team_b: Name of the second team.
        model: Trained `PoissonRegressor` from `train_model`.
        scaler: `StandardScaler` fitted alongside the model.
        features_df: Full per-team feature history; the latest row per
            team is used as that team's current form.

    Returns:
        A tuple `(goals_a, goals_b)` of non-negative integer goal counts.
    """
    # Take each team's most recent feature row as their current form.
    mrf_a = features_df[features_df["team"] == team_a].sort_values("date", ascending=False).iloc[0]
    mrf_b = features_df[features_df["team"] == team_b].sort_values("date", ascending=False).iloc[0]

    team_a_features = mrf_a[FEATURE_COLS]
    team_b_features = mrf_b[FEATURE_COLS]

    # Apply the exact scaling that was fit on the training set.
    team_a_scaled = scaler.transform(pd.DataFrame([team_a_features], columns=FEATURE_COLS))
    team_b_scaled = scaler.transform(pd.DataFrame([team_b_features], columns=FEATURE_COLS))

    # Poisson regression predicts the expected goals (rate parameter lambda).
    lambda_a = model.predict(team_a_scaled)[0]
    lambda_b = model.predict(team_b_scaled)[0]

    # Poisson sampling — final scores are drawn independently per side.
    goals_a = np.random.poisson(lambda_a)
    goals_b = np.random.poisson(lambda_b)

    return goals_a, goals_b

def simulate_group(group_name, teams, model, scaler, features_df):
    """Simulate every match in a group and return the final standings.

    Plays each of the (n choose 2) pairings exactly once, accumulating
    wins/draws/losses, goals for/against, goal difference, and points
    (3 for a win, 1 for a draw). Standings are sorted by points, then
    goal difference, then goals for — matching FIFA tiebreakers up to
    the head-to-head step (head-to-head is not applied here).

    Args:
        group_name: Group letter (informational; only used by callers).
        teams: List of team names in the group.
        model: Trained Poisson model.
        scaler: Matching feature scaler.
        features_df: Per-team feature history.

    Returns:
        A DataFrame of standings with columns `team`, `played`, `wins`,
        `draws`, `losses`, `goals_for`, `goals_against`,
        `goal_difference`, and `points`, sorted from first to last.
    """
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
    # Round-robin: every unordered pair plays exactly once.
    matches = combinations(teams, 2)
    for match in matches:
        team_a = match[0]
        team_b = match[1]
        goals_a, goals_b = simulate_match(team_a, team_b, model, scaler, features_df)

        # Update the per-team aggregates for both sides.
        group_df.loc[group_df["team"] == team_a, "played"] += 1
        group_df.loc[group_df["team"] == team_b, "played"] += 1
        group_df.loc[group_df["team"] == team_a, "goals_for"] += goals_a
        group_df.loc[group_df["team"] == team_b, "goals_for"] += goals_b

        group_df.loc[group_df["team"] == team_a, "goals_against"] += goals_b
        group_df.loc[group_df["team"] == team_b, "goals_against"] += goals_a

        group_df.loc[group_df["team"] == team_a, "goal_difference"] += goals_a - goals_b
        group_df.loc[group_df["team"] == team_b, "goal_difference"] += goals_b - goals_a

        # Award points: 3 for a win, 1 each for a draw.
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
        
    # Final group ranking by FIFA tiebreakers (points > GD > GF).
    group_df = group_df.sort_values(
        ["points", "goal_difference", "goals_for"],
        ascending=False
    ).reset_index(drop=True)

    return group_df

def get_qualifiers(all_standings):
    """Resolve the 32 teams that advance to the Round of 32.

    The 2026 format expands the knockout stage to 32 teams: all 12 group
    winners, all 12 runners-up, and the 8 best third-placed teams ranked
    across groups by points, then goal difference, then goals for.

    Args:
        all_standings: Mapping from group letter to the sorted standings
            DataFrame returned by `simulate_group`.

    Returns:
        A dict with three keys:
          - `group_winners`: list of 12 standing rows (first place per group)
          - `group_runners_up`: list of 12 standing rows (second place)
          - `best_third`: list of 8 team names (best third-placed teams)
    """
    group_winners = []
    group_runners_up = []
    third_place_teams = []

    for group_name, standings in all_standings.items():
        # 1st place auto-qualifies as a group winner.
        group_winner = standings.iloc[0]
        group_winners.append(group_winner)

        # 2nd place auto-qualifies as a runner-up.
        runners_up = standings.iloc[1]
        group_runners_up.append(runners_up)

        # 3rd place is pooled across all 12 groups and ranked at the end.
        third = standings.iloc[2]
        third_place_teams.append(third)

        # NOTE: this re-sort runs every iteration so the final value of
        # `best_third` after the loop is the correct ranking across all groups.
        third_place_df = pd.DataFrame(third_place_teams)
        third_place_df = third_place_df.sort_values(
            ["points", "goal_difference", "goals_for"],
            ascending=False
        ).reset_index(drop=True)

        best_third = third_place_df.iloc[:8]["team"].tolist()

    return {
        "group_winners": group_winners,
        "group_runners_up": group_runners_up,
        "best_third": best_third
    }
