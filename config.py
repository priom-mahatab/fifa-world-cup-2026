BASE_ELO = 1500
LOSS = 0.0
WIN = 1.0
TIE = 0.5
K = 20

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