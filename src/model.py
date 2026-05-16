"""Trains the Poisson goal-scoring model used by the simulator."""

from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler
from config import FEATURE_COLS, WORLD_CUP_TEAMS

def train_model(features_df):
    """Fit a Poisson regressor that predicts a team's expected goals.

    Training is restricted to matches involving the 2026 World Cup
    participants so the model concentrates capacity on the teams it
    will be used to simulate. Per-match `sample_weight` (importance x
    recency) is passed through so recent / high-stakes matches dominate
    the fit.

    Args:
        features_df: Output of `compute_features` — must contain
            `FEATURE_COLS`, `goals_scored`, `team`, and `sample_weight`.

    Returns:
        A tuple `(model, scaler)` where `model` is the fitted
        `PoissonRegressor` and `scaler` is the `StandardScaler` fitted
        on the training features. Both must be applied together at
        prediction time.
    """
    # Restrict training data to matches involving World Cup participants
    # and rows that actually have a goal count (drops the unplayed/NaN ones).
    train_df = features_df[
        (features_df["team"].isin(WORLD_CUP_TEAMS)) &
        (features_df["goals_scored"].notna())
    ]
    scaler = StandardScaler()
    X = train_df[FEATURE_COLS]
    y = train_df["goals_scored"]

    # Scale features so the L2 penalty (alpha=0.1) treats them comparably.
    X_scaled = scaler.fit_transform(X)
    sample_weight = train_df["sample_weight"]
    model = PoissonRegressor(alpha=0.1, max_iter=1000)
    model.fit(X_scaled, y, sample_weight=sample_weight)
    # print(train_df.shape)
    # print(train_df[FEATURE_COLS].isnull().sum())
    # print(y.describe())
    # print(model)

    return model, scaler
