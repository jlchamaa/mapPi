from .base import Base, Auth, ScoreboardSubscription
from .nba import NBAHandler
from .mlb import MLBHandler
from .nfl import NFLHandler

all_handlers = [
    Base,
    Auth,
    ScoreboardSubscription,
    # NBA,
    # NFL,
    # MLB
]
