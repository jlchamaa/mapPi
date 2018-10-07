var mlbDict={
    'ATL': 'Atlanta Braves',
    'MIA': 'Miami Marlins',
    'BOS': 'Boston Red Sox',
    'BAL': 'Baltimore Orioles',
    'LAD': 'Los Angeles Dodgers',
    'PHI': 'Philadelphia Phillies',
    'MIN': 'Minnesota Twins',
    'TOR': 'Toronto Blue Jays',
    'PIT': 'Pittsburgh Pirates',
    'CLE': 'Cleveland Indians',
    'NYY': 'New York Yankees',
    'TB' : 'Tampa Bay Rays',
    'STL': 'St. Louis Cardinals',
    'CIN': 'Cincinnati Reds',
    'SD' : 'San Diego Padres',
    'NYM': 'New York Mets',
    'OAK': 'Oakland Athletics',
    'TEX': 'Texas Rangers',
    'ARI': 'Arizona Diamondbacks',
    'CHC': 'Chicago Cubs',
    'WAS': 'Washington Nationals',
    'MIL': 'Milwaukee Brewers',
    'DET': 'Detroit Tigers',
    'KC' : 'Kansas City Royals',
    'HOU': 'Houston Astros',
    'COL': 'Colorado Rockies',
    'CHW': 'Chicago White Sox',
    'LAA': 'Los Angeles Angels',
    'SF' : 'San Francisco Giants',
    'SEA': 'Seattle Mariners'
}
const WebSocket = require('ws');

const ws = new WebSocket('wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket');
mlbGames=['empty'];
mlbScore={};

function subscribeToGame(gameID){
    var obj = {"cmd":"subscribe","topics":gameID};
    //console.log(obj);
    var request = JSON.stringify(JSON.stringify(obj)); //THIS THING WANTS A DOUBLE STRING IDK WHY
    ws.send(request);
}
function subscribeScoreboard(){
    var obj = {"cmd":"subscribe","topics":["/mlb/scoreboard"]};
    var request = JSON.stringify(JSON.stringify(obj)); //THIS THING WANTS A DOUBLE STRING IDK WHY
    ws.send(request);
}
function auth(){
    var message= {"cmd":"login","access_token":"64d1553ce024ab863adf69cff277b1f2ed75d961"};
    var request = JSON.stringify(JSON.stringify(message));
    ws.send(request);
}

function updateMlbScore(teamAbbr,newScore){
    if(teamAbbr in mlbScore){
        if(mlbScore[teamAbbr]!=newScore){
            var delta = newScore - mlbScore[teamAbbr];
            if(delta > 0){
                console.log(mlbDict[teamAbbr] + "+" + delta + ", "+ newScore);
                mlbScore[teamAbbr]=newScore;
            }
        }
    }
    else{
        mlbScore[teamAbbr]=newScore;
    }
}

ws.on('open', function open() {
    //console.log('connected')
});

ws.on('close', function close() {
    console.log('close')
});

ws.on('error', function(error) {
    console.log('WebSocket Error: ' + error);
  });

ws.on('message', function incoming(data) {
    if(data == 'o'){
        auth();
    }
    else if(data.includes('authorized')){
        subscribeScoreboard();
    }       
    else if(data.length < 5){
        //console.log(data);
    }
    else{
        var slicedData = data.slice(2,-1); //turns a[json] into json
        var temp=JSON.parse(slicedData);
        var obj=JSON.parse(temp);
        //console.log(obj);

        if(data.includes('scoreboard') && ! data.includes('update') && ! data.includes('subscribe')){ //real scoreboard, not subscription confirmation
            var games=obj.body.games;
            if(mlbGames[0]!=games[0].abbr){
                //we're either filling the 'empty' array, or we have a new day
                //so empty the array and continue on
                //console.log('fresh refill');
                mlbGames=[];
                for(var game in games){
                    var gameID = games[game].abbr
                    mlbGames.push(gameID);
                    subscribeToGame("/mlb/gametracker/"+gameID+"/ts");
                }
            }
            //else{console.log('no refill');} //data was already present, no refill
        }
        if(data.includes('gametracker') && data.includes('update') && ! data.includes('subscribe')){
            var numOfTeams=obj.body.length;
            for (var i=0;i<numOfTeams;i++){
                updateMlbScore(obj.body[i].abbr,parseInt(obj.body[i].batting.runs));
            }
        }
    }
});

