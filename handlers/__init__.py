from .scoreboard_subscription import ScoreboardSubscription
from .auth import Auth
from .logger import Logger
from .nba import NBALeague, NBAScore
from .nfl import NFLLeague, NFLScore

all_handlers = [
    ScoreboardSubscription,
    Auth,
    Logger,
    NFLLeague, NFLScore,
    # MLBLeague,
    NBALeague, NBAScore,
]
