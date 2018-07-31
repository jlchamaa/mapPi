var nbaDict={
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
    'STL': 'St. Louis Carindals',
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
    'KC' : 'Kansas City Rotals',
    'HOU': 'Houston Astros',
    'COL': 'Colorado Rockies',
    'CHW': 'Chicago White Sox',
    'LAA': 'Los Angeles Angels',
    'SF' : 'San Francisco Giants',
    'SEA': 'Seattle Mariners'
}
const WebSocket = require('ws');

const ws = new WebSocket('wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket');
nbaGames=['empty'];
nbaScore={};

function subscribeToGame(gameID){
    var obj = {"cmd":"subscribe","topics":gameID};
    console.log(obj);
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

function updateNBAScore(teamAbbr,newScore){
    if(nbaScore[teamAbbr]){
        if(nbaScore[teamAbbr]!=newScore){
            var delta = newScore - nbaScore[teamAbbr];
            if(delta > 0){
                console.log(nbaDict[teamAbbr] + "+" + delta + ", "+ newScore);
                nbaScore[teamAbbr]=newScore;
            }
        }
    }
    else{
        nbaScore[teamAbbr]=newScore;
        //console.log(nbaDict[teamAbbr] + "+" + newScore);
    }
}

ws.on('open', function open() {
    console.log('connected')
});

ws.on('close', function close() {
    console.log('close')
});

ws.on('error', function(error) {
    console.log('WebSocket Error: ' + error);
  });

ws.on('message', function incoming(data) {
    console.log(data);
    if(data == 'o'){
        auth();
    }
    if(data.includes('authorized')){
        subscribeScoreboard();
    }       
    
    if(data.includes('scoreboard') && ! data.includes('update') && ! data.includes('subscribe')){ //real scoreboard, not subscription confirmation
        var slicedData = data.slice(2,-1); //turns a[json] into json
        var temp=JSON.parse(slicedData);
        var obj=JSON.parse(temp);
        var games=obj.body.games;
        if(nbaGames[0]!=games[0].abbr){
            //we're either filling the 'empty' array, or we have a new day
            //so empty the array and continue on
            //console.log('fresh refill');
            nbaGames=[];
            for(var game in games){
                var gameID = games[game].abbr
                nbaGames.push(gameID);
                subscribeToGame("/nba/gametracker/"+gameID+"/ts");
            }
        }
        //else{console.log('no refill');} //data was already present, no refill
        console.log(nbaGames);

    }
    
    if(data.includes('gametracker') && data.includes('update') && ! data.includes('subscribe')){
        var slicedData = data.slice(2,-1); //turns a[json] into json
        var temp=JSON.parse(slicedData);
        var obj=JSON.parse(temp);
        var numOfTeams=obj.body.length;
        for (var i=0;i<numOfTeams;i++){
            updateNBAScore(obj.body[i].abbr,parseInt(obj.body[i].stats.points));
        }
    }
});

