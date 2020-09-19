var nbaDict={
'DAL':'Dallas Cowboys',
'NYG':'New York Giants',
'PHI':'Philadelphia Eagles',
'WAS':'Washington Redskins',
'BUF':'Buffalo Bills',
'MIA':'Miami Dolphins',
'NE':'New England Patriots',
'NYJ':'New York Jets',
'ARI':'Arizona Cardinals',
'LAR':'Los Angeles Rams',
'SF':'San Francisco 49ers',
'SEA':'Seattle Seahawks',
'DEN':'Denver Broncos',
'KC':'Kansas City Chiefs',
'LAC':'Los Angeles Chargers',
'LV':'Las Vegas Raiders',
'CHI':'Chicago Bears',
'DET':'Detroit Lions',
'GB':'Green Bay Packers',
'MIN':'Minnesota Vikings',
'BAL':'Baltimore Ravens',
'CIN':'Cincinnati Bengals',
'CLE':'Cleveland Browns',
'PIT':'Pittsburgh Steelers',
'ATL':'Atlanta Falcons',
'CAR':'Carolina Panthers',
'NO':'New Orleans Saints',
'TB':'Tampa Bay Buccaneers',
'HOU':'Houston Texans',
'IND':'Indianapolis Colts',
'JAC':'Jacksonville Jaguars',
'TEN':'Tennessee Titans '
}
const WebSocket = require('ws');

const ws = new WebSocket('wss://torq.cbssports.com/torq/handler/117/7v5ku21t/websocket');
nbaGames=['empty'];
nbaScore={};

function subscribeToGame(gameID){
    var obj = {"cmd":"subscribe","topics":gameID};
    var request = JSON.stringify(JSON.stringify(obj)); //THIS THING WANTS A DOUBLE STRING IDK WHY
    ws.send(request);
}
function subscribeScoreboard(){
    var obj = {"cmd":"subscribe","topics":["/nfl/scoreboard"]};
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
                console.log(nbaDict[teamAbbr] + "+" + delta+", "+ newScore);
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
    //console.log('connected')
});

ws.on('close', function close() {
    console.log('close')
});

ws.on('error', function(error) {
    console.log('WebSocket Error: ' + error);
  });

ws.on('message', function incoming(data) {
    //console.log(data);
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
                subscribeToGame("/nfl/gametracker/"+gameID+"/scores");
            }
        }
        //else{console.log('no refill');} //data was already present, no refill
        //console.log(nbaGames);

    }
    
    if(data.includes('gametracker') && data.includes('update') && ! data.includes('subscribe')){
        var slicedData = data.slice(2,-1); //turns a[json] into json
        var temp=JSON.parse(slicedData);
        var obj=JSON.parse(temp);
        var teams = data.match(/([A-Z]{2,3})@([A-Z]{2,3})/);
        updateNBAScore(teams[1],obj.body[0].away_score);
        updateNBAScore(teams[2],obj.body[0].home_score);
    }
    
});
