from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler
from config import FEATURE_COLS, WORLD_CUP_TEAMS

def train_model(features_df):
    train_df = features_df[
        (features_df["team"].isin(WORLD_CUP_TEAMS)) &
        (features_df["goals_scored"].notna())
    ]
    scaler = StandardScaler()
    X = train_df[FEATURE_COLS]
    y = train_df["goals_scored"]

    X_scaled = scaler.fit_transform(X)
    sample_weight = train_df["sample_weight"]
    model = PoissonRegressor(alpha=0.1, max_iter=1000)
    model.fit(X_scaled, y, sample_weight=sample_weight)
    print(train_df.shape)
    print(train_df[FEATURE_COLS].isnull().sum())
    print(y.describe())
    print(model)

    return model, scaler
