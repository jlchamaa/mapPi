console.log("help me");

async function refresh() {
    console.log("Called refresh");
    const response = await fetch("/scoreboard");
    const data = await response.json();
    console.log(data);
    update("nfl", "SEA", "5");
}

function update(league, team, score) {
    const team_id = league + "." + team;
    const div = document.getElementById(team_id)
    div.innerHTML = team + ": " + score;
}
