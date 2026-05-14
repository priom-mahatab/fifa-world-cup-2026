import pandas as pd
import numpy as np
from config import FEATURE_COLS

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