from .auth import Auth
from .logger import Logger
from .mlb import MLBLeague, MLBScore
from .nba import NBALeague, NBAScore
from .nfl import NFLLeague, NFLScore

all_handlers = [
    Logger,
    Auth,
    MLBLeague, MLBScore,
    NBALeague, NBAScore,
    NFLLeague, NFLScore,
]
