import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

BASE_ELO = 1500
LOSS = 0.0
WIN = 1.0
TIE = 0.5
K = 20

# Set the path to the file you'd like to load
file_path = "results.csv"

# Load the latest version
df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "martj42/international-football-results-from-1872-to-2017",
  file_path)

# print("First 5 records:", df.head())
# print(df.info())
# print(df.describe())
# print(df["tournament"].value_counts())
# print(df.isnull().sum())

# tournaments = df["tournament"].unique()
# for tournament in tournaments:
#     print(tournament)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["tournament_weight"] = df["tournament"].map({
    "FIFA World Cup": 1.0,
    "Copa América": 0.8,
    "UEFA Euro": 0.8,
    "African Cup of Nations": 0.8,
    "AFC Asian Cup": 0.8,
    "FIFA World Cup qualification": 0.6,
    "UEFA Nations League": 0.6,
    "CONCACAF Nations League": 0.6,
    "Gold Cup": 0.6,
    "Gulf Cup": 0.6,
    "AFF Championship": 0.6,
    "Arab Cup": 0.4,
    "COSAFA Cup": 0.4,
    "CECAFA Cup": 0.4,
    "African Cup of Nations qualification": 0.4,
    "UEFA Euro qualification": 0.4,
    "Copa América qualification": 0.4,
    "AFC Asian Cup qualification": 0.4,
    "Friendly": 0.2
}).fillna(0.25)

# print(df["tournament_weight"].isnull().sum())
# print(df[df["tournament_weight"].isnull()]["tournament"].value_counts().head(20))

def get_recency_weight(date):
    if date >= pd.Timestamp('2022-11-20'):  # 2022 World Cup start date
        return 1.0
    elif date >= pd.Timestamp('2018-06-14'):  # 2018 World Cup start date
        return 0.7
    elif date >= pd.Timestamp('2014-06-12'):  # 2014 World Cup start date
        return 0.4
    elif date >= pd.Timestamp('2010-06-11'):  # 2010 World Cup start date
        return 0.2
    else:
        return 0.0

df["recency_weight"] = df["date"].apply(get_recency_weight)
df["sample_weight"] = df["tournament_weight"] * df["recency_weight"]

# Filter out matches with zero weight
df = df[df["recency_weight"] > 0]
df = df.dropna(subset=["home_score", "away_score"]).copy()

print(df.head())
print(df.tail())
print(df.shape)
print(df["sample_weight"].isnull().sum())
print(df["sample_weight"].describe())
print(df["date"].min(), df["date"].max())

# elo rating
elo_ratings = {}
elo_records = []

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
    expected_result = 1 / (1 + 10 ** ((opponent_elo - team_elo) / 400))
    return expected_result

def update_elo(team_elo, opponent_elo, actual_result, tournament_weight, goal_diff):
    goal_diff_multiplier = get_goal_diff_multiplier(goal_diff)
    expected_result = get_expected_result(team_elo, opponent_elo)

    new_elo = team_elo + K * goal_diff_multiplier * tournament_weight * (actual_result - expected_result)
    return new_elo


df = df.sort_values("date").reset_index(drop=True)

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

    home_elo = elo_ratings.get(home)
    away_elo = elo_ratings.get(away)

    home_result = None
    away_result = None

    if home_score > away_score:
        home_result = WIN
        away_result = LOSS

    elif home_score < away_score:
        home_result = LOSS
        away_result = WIN

    else:
        home_result, away_result = TIE, TIE

    new_home_elo = update_elo(home_elo, away_elo, home_result, tournament_weight, goal_difference)
    new_away_elo = update_elo(away_elo, home_elo, away_result, tournament_weight, goal_difference)

    elo_ratings[home] = new_home_elo
    elo_ratings[away] =  new_away_elo

    home_record = {
        "date": date,
        "team": home,
        "opponent": away,
        "elo_before": home_elo,
        "elo_after": new_home_elo,
        "actual_result": home_result,
        "goal_diff": goal_difference,
        "tournament_weight": tournament_weight
    }

    away_record = {
        "date": date,
        "team": away,
        "opponent": home,
        "elo_before": away_elo,
        "elo_after": new_away_elo,
        "actual_result": away_result,
        "goal_diff": goal_difference,
        "tournament_weight": tournament_weight
    }

    elo_records.append(home_record)
    elo_records.append(away_record)

elo_df = pd.DataFrame(elo_records)
print(elo_df.shape)
print(elo_df.head())
print(sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)[:10])

print(df[df["home_score"].isna()].shape)
print(elo_df[elo_df["elo_before"].isna()].shape)
print(df.shape)
