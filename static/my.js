console.log("help me");

async function refresh() {
    console.log("Called refresh");
    const response = await fetch("/scoreboard");
    const data = await response.json();
    const nba = data.nba;
    for (team in nba){
      update("nba", team, nba[team]);
    }
    const mlb = data.mlb;
    for (team in mlb){
      update("mlb", team, mlb[team]);
    }
    const nfl = data.nfl;
    for (team in nfl){
      update("nfl", team, nfl[team]);
    }
}

function update(league, team, score) {
    const team_id = league + "." + team;
    const div = document.getElementById(team_id);
    if (score === null) {
        div.style.backgroundColor = "white"
    }
    else {
        div.style.backgroundColor = "lightgreen"
        div.innerHTML = team + ": " + score;
    }
}
