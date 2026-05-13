import pandas as pd

from config import BASE_ELO, WIN, LOSS, TIE, K


def get_goal_diff_multiplier(goal_diff):
    if goal_diff == 1:
        return 1.0
    if goal_diff == 2:
        return 1.5
    if goal_diff == 3:
        return 1.75
    else:
        return 2.0


def get_expected_result(team_elo, opponent_elo):
    return 1 / (1 + 10 ** ((opponent_elo - team_elo) / 400))


def update_elo(team_elo, opponent_elo, actual_result, tournament_weight, goal_diff):
    goal_diff_multiplier = get_goal_diff_multiplier(goal_diff)
    expected_result = get_expected_result(team_elo, opponent_elo)
    new_elo = team_elo + K * goal_diff_multiplier * tournament_weight * (actual_result - expected_result)
    return new_elo


def compute_elo(df):
    elo_ratings = {}
    elo_records = []

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        date = row["date"]
        home_score = row["home_score"]
        away_score = row["away_score"]
        goal_difference = abs(home_score - away_score)
        tournament_weight = row["tournament_weight"]

        if home not in elo_ratings:
            elo_ratings[home] = BASE_ELO
        if away not in elo_ratings:
            elo_ratings[away] = BASE_ELO

        home_elo = elo_ratings[home]
        away_elo = elo_ratings[away]

        if home_score > away_score:
            home_result, away_result = WIN, LOSS
        elif home_score < away_score:
            home_result, away_result = LOSS, WIN
        else:
            home_result, away_result = TIE, TIE

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