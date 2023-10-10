import logging
from handlers.base import Handler
log = logging.getLogger("mappy")


class NBAScoreboard(Handler):
    def is_relevant(self, obj):
        return (
            obj.get("topic") == "/nba/scoreboard"
            and obj.get("eventType") in ["update", "setState"]
        )

    async def handle(self, obj, ws):
        log.info("NBA handle")
        

    async def handle_nba(self, data, ws):
        topic = data.get("topic", "")
        event_type = data.get("eventType", "")
        if "scoreboard" in topic:
            # populate scoreboard
            if event_type == "setState":
                league = topic[1:4]
                if "body" not in data:
                    self.logwrite(f"bodyless data for {topic}")
                    self.logwrite(data)
                    return
                for game_info in data["body"]["games"]:
                    if "abbr" not in game_info:
                        self.logwrite("We didn't have an abbr??")
                        self.logwrite(topic)
                        continue
                    game_id = game_info["abbr"]
                    game_topic = "/{}/gametracker/{}/ts".format(league, game_id)
                    if game_topic in self.sb.games:
                        # await self.emit(self.Updatemessage(self, "topics"))
                        continue
                    self.sb.games.add(game_topic)
                    self.logwrite("subscribing to {}".format(game_topic))
                    await subscribe_to_game_topic(ws, game_topic)
            else:
                # we got the scoreboard, so get out
                await unsubscribe_topic(ws, topic)
                self.logwrite(f"Unsubscribed {topic}")
        elif "gametracker" in topic:
            try:
                if event_type == "":
                    return
                if event_type == "setState":
                    teams = data["body"]["ts"]
                elif event_type == "update":
                    teams = data["body"]
                else:
                    self.logwrite(event_type)
                    return
                for team_data in teams:
                    team_id = team_data["abbr"]
                    team_score = int(team_data["stats"]["points"])
                    r = self.sb.record_score("nba", team_id, team_score)
                    self.logwrite(r)
                    # await self.emit(self.Updatemessage(self, "nba"))
            except Exception as e:
                self.logwrite("Problem in the NBA")
                self.logwrite(traceback.format_exc())
                self.logwrite(json.dumps(data, indent=2, sort_keys=True))
                self.logwrite(e)
        else:
            self.logwrite("nba 4")
            self.logwrite(data)

