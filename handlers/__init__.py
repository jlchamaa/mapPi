from .base import Base, Auth, ScoreboardSubscription
from .nba import NBALeague, NBAScore
from .mlb import MLBLeague
from .nfl import NFLLeague, NFLScore

all_handlers = [
    Base,
    Auth,
    ScoreboardSubscription,
    NFLLeague, NFLScore,
    # MLBLeague,
    NBALeague, NBAScore,
]
