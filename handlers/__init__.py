from .scoreboard_subscription import ScoreboardSubscription
from .auth import Auth
from .nba import NBALeague, NBAScore
from .nfl import NFLLeague, NFLScore

all_handlers = [
    ScoreboardSubscription,
    Auth,
    NFLLeague, NFLScore,
    # MLBLeague,
    NBALeague, NBAScore,
]
