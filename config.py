BASE_ELO = 1500
LOSS = 0.0
WIN = 1.0
TIE = 0.5
K = 20

FEATURE_COLS = [
    "elo_before",
    "win_rate_10", "win_rate_20",
    "avg_goals_scored_10", "avg_goals_scored_20",
    "avg_goals_conceded_10", "avg_goals_conceded_20",
    "clean_sheet_rate_10", "clean_sheet_rate_20"
]

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

DEFAULT_TOURNAMENT_WEIGHT = 0.25

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