console.log("help me");

async function refresh() {
    console.log("Called refresh");
    const response = await fetch("/scoreboard");
    const data = await response.json();
    const nba = data.nba;
    console.log(nba);
    for (team in nba){
      update("nba", team, nba[team]);
    }
}

function update(league, team, score) {
    console.log(league + team + score)
    const team_id = league + "." + team;
    const div = document.getElementById(team_id)
    div.innerHTML = team + ": " + score;
}
