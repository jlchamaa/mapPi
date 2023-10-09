console.log("help me");

async function new_lines() {
    console.log("Called new_lines");
    const response = await fetch("/new_lines");
    const data = await response.json();
}

async function new_scores() {
    console.log("Called new_scores");
    const response = await fetch("/new_scores");
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

// const the_timer = setInterval(new_lines, 5000)
// const the_timer_2 = setInterval(new_scores, 5000)
