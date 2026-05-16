"""Project-wide configuration constants for the World Cup simulator.

Centralises ELO parameters, model feature columns, tournament importance
weights, team-name normalisation rules, and the 2026 tournament bracket
structure so every module reads from a single source of truth.
"""

# Elo rating constants
BASE_ELO = 1500        # Default rating assigned to a team the first time it appears
LOSS = 0.0             # Actual-result encoding for a loss
WIN = 1.0              # Actual-result encoding for a win
TIE = 0.5              # Actual-result encoding for a draw
K = 20                 # Base K-factor controlling how quickly Elo updates after each match

# Columns used as inputs to the Poisson goal-scoring model
FEATURE_COLS = [
    "elo_before",
    "win_rate_10", "win_rate_20",
    "avg_goals_scored_10", "avg_goals_scored_20",
    "avg_goals_conceded_10", "avg_goals_conceded_20",
    "clean_sheet_rate_10", "clean_sheet_rate_20"
]

# Importance weights for each competition; major tournaments carry more
# weight in both the Elo update and the Poisson training sample.
TOURNAMENT_WEIGHTS = {
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
    "Friendly": 0.2,
}

# Fallback weight for any tournament not explicitly listed above
DEFAULT_TOURNAMENT_WEIGHT = 0.25

# Maps the team names used in the Kaggle dataset to the canonical names
# used elsewhere in the project (e.g. in GROUPS and WORLD_CUP_TEAMS).
TEAM_NAME_MAP = {
    "IR Iran": "Iran",
    "Korea Republic": "South Korea",
    "Côte d'Ivoire": "Ivory Coast",
    "Türkiye": "Turkey",
    "Congo DR": "DR Congo",
    "Cabo Verde": "Cape Verde",
    "Czechia": "Czech Republic",
    "Curaçao": "Curaçao",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "USA": "United States",
}

# All 48 nations that have qualified (or are projected to qualify)
# for the 2026 FIFA World Cup, grouped by confederation.
WORLD_CUP_TEAMS = [
    # Co-hosts
    "Canada", "Mexico", "United States",
    # AFC
    "Australia", "Iraq", "Iran", "Japan", "Jordan",
    "South Korea", "Qatar", "Saudi Arabia", "Uzbekistan",
    # CAF
    "Algeria", "Cape Verde", "DR Congo", "Ivory Coast", "Egypt",
    "Ghana", "Morocco", "Senegal", "South Africa", "Tunisia",
    # CONCACAF
    "Curaçao", "Haiti", "Panama",
    # CONMEBOL
    "Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay",
    # OFC
    "New Zealand",
    # UEFA
    "Austria", "Belgium", "Bosnia and Herzegovina", "Croatia", "Czech Republic",
    "England", "France", "Germany", "Netherlands", "Norway", "Portugal",
    "Scotland", "Spain", "Sweden", "Switzerland", "Turkey",
]

# Group-stage draw for the 2026 World Cup: 12 groups of 4 teams each.
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Round-of-32 bracket pairings. Each tuple is (slot_a, slot_b) where slot
# identifiers encode the seed in the format "<rank><group(s)>" — e.g. "1E"
# means the winner of Group E, and "3ABCDF" means the best third-placed
# team out of Groups A, B, C, D, or F as determined by the FIFA matrix.
ROUND_OF_32 = [
    ("1E", "3ABCDF"),
    ("1I", "3CDFGH"),
    ("2A", "2B"),
    ("1F", "2C"),
    ("2K", "2L"),
    ("1H", "2J"),
    ("1D", "3BEFIJ"),
    ("1G", "3AEHIJ"),
    ("1C", "2F"),
    ("2E", "2I"),
    ("1A", "3CEFHI"),
    ("1L", "3EHIJK"),
    ("1J", "2H"),
    ("2D", "2G"),
    ("1B", "3EFGIJ"),
    ("1K", "3DEIJL"),
]