"""Elo rating computation for international football teams.

Implements a World Football Elo-style update with a goal-difference
multiplier and per-tournament importance weighting. Walks the historical
match data chronologically to produce both a per-match Elo history
DataFrame and the latest rating for each team.
"""

import pandas as pd

from config import BASE_ELO, WIN, LOSS, TIE, K


def get_goal_diff_multiplier(goal_diff):
    """Return the Elo K-factor multiplier for a given absolute goal difference.

    Larger margins of victory inflate the rating change, capped at 2.0
    once the goal difference reaches 4 or more.

    Args:
        goal_diff: Absolute goal difference of the match (>= 0).

    Returns:
        A float multiplier: 1.0 for a 1-goal margin, 1.5 for 2, 1.75 for
        3, and 2.0 for any larger margin (including a draw).
    """
    if goal_diff == 1:
        return 1.0
    if goal_diff == 2:
        return 1.5
    if goal_diff == 3:
        return 1.75
    else:
        return 2.0


def get_expected_result(team_elo, opponent_elo):
    """Standard Elo expected-score formula.

    Args:
        team_elo: Current rating of the team whose expected score we want.
        opponent_elo: Current rating of the opponent.

    Returns:
        Expected score in [0, 1] — 0.5 when ratings are equal, higher
        when the team is favoured.
    """
    return 1 / (1 + 10 ** ((opponent_elo - team_elo) / 400))


def update_elo(team_elo, opponent_elo, actual_result, tournament_weight, goal_diff):
    """Compute a team's new Elo rating after a single match.

    Args:
        team_elo: Rating before the match for the team being updated.
        opponent_elo: Pre-match rating of the opponent.
        actual_result: 1.0 for a win, 0.5 for a draw, 0.0 for a loss.
        tournament_weight: Importance weight of the competition (see
            `config.TOURNAMENT_WEIGHTS`).
        goal_diff: Absolute goal difference of the final score.

    Returns:
        The team's updated Elo rating as a float.
    """
    goal_diff_multiplier = get_goal_diff_multiplier(goal_diff)
    expected_result = get_expected_result(team_elo, opponent_elo)
    # Standard Elo update, with K scaled by goal-difference and tournament weight.
    new_elo = team_elo + K * goal_diff_multiplier * tournament_weight * (actual_result - expected_result)
    return new_elo


def compute_elo(df):
    """Run the chronological Elo walk over every match in `df`.

    For each match the home and away ratings are updated and two rows
    (one per team) are appended to the running history. Teams seen for
    the first time are initialised at `BASE_ELO`.

    Args:
        df: DataFrame of matches sorted by date, with columns
            `home_team`, `away_team`, `date`, `home_score`,
            `away_score`, and `tournament_weight`.

    Returns:
        A tuple `(elo_df, elo_ratings)` where `elo_df` is a long-format
        DataFrame with one row per team per match (containing the
        pre- and post-match rating, opponent, result, goal difference,
        and tournament weight) and `elo_ratings` is a dict mapping
        team name to its final rating after the last match.
    """
    elo_ratings = {}   # Latest rating per team, updated in-place during the walk.
    elo_records = []   # Long-format history; two appends per match (home, away).

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        date = row["date"]
        home_score = row["home_score"]
        away_score = row["away_score"]
        goal_difference = abs(home_score - away_score)
        tournament_weight = row["tournament_weight"]

        # Initialise any team we haven't seen before at the base rating.
        if home not in elo_ratings:
            elo_ratings[home] = BASE_ELO
        if away not in elo_ratings:
            elo_ratings[away] = BASE_ELO

        home_elo = elo_ratings[home]
        away_elo = elo_ratings[away]

        # Encode the match result from each team's perspective.
        if home_score > away_score:
            home_result, away_result = WIN, LOSS
        elif home_score < away_score:
            home_result, away_result = LOSS, WIN
        else:
            home_result, away_result = TIE, TIE

        # Both ratings must be updated using the *pre-match* values of the
        # opponent — that's why we capture home_elo/away_elo above.
        new_home_elo = update_elo(home_elo, away_elo, home_result, tournament_weight, goal_difference)
        new_away_elo = update_elo(away_elo, home_elo, away_result, tournament_weight, goal_difference)

        elo_ratings[home] = new_home_elo
        elo_ratings[away] = new_away_elo

        elo_records.append({
            "date": date,
            "team": home,
            "opponent": away,
            "elo_before": home_elo,
            "elo_after": new_home_elo,
            "actual_result": home_result,
            "goal_diff": goal_difference,
            "tournament_weight": tournament_weight,
        })

        elo_records.append({
            "date": date,
            "team": away,
            "opponent": home,
            "elo_before": away_elo,
            "elo_after": new_away_elo,
            "actual_result": away_result,
            "goal_diff": goal_difference,
            "tournament_weight": tournament_weight,
        })

    elo_df = pd.DataFrame(elo_records)
    return elo_df, elo_ratings