from .base import Base, Auth, ScoreboardSubscription
from .nba import NBAScoreboard, NBAScore
from .mlb import MLBScoreboard
from .nfl import NFLScoreboard, NFLScore

all_handlers = [
    Base,
    Auth,
    ScoreboardSubscription,
    # NFLScoreboard,
    MLBScoreboard,
    NBAScoreboard, NBAScore
    # NBA,
    # NFL,
    # MLB
]
