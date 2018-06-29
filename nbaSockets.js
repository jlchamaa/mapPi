var nbaDict={
'BOS':'Boston Celtics',
'BKN':'Brooklyn Nets',
'NY':'New York Knicks',
'PHI':'Philadelphia 76ers',
'TOR':'Toronto Raptors',
'GS':'Golden State Warriors',
'LAC':'LA Clippers',
'LAL':'Los Angeles Lakers',
'PHO':'Phoenix Suns',
'SAC':'Sacramento Kings',
'CHI':'Chicago Bulls',
'CLE':'Cleveland Cavaliers',
'DET':'Detroit Pistons',
'IND':'Indiana Pacers',
'MIL':'Milwaukee Bucks',
'DAL':'Dallas Mavericks',
'HOU':'Houston Rockets',
'MEM':'Memphis Grizzlies',
'NO':'New Orleans Pelicans',
'SA':'San Antonio Spurs',
'ATL':'Atlanta Hawks',
'CHA':'Charlotte Hornets',
'MIA':'Miami Heat',
'ORL':'Orlando Magic',
'WAS':'Washington Wizards',
'DEN':'Denver Nuggets',
'MIN':'Minnesota Timberwolves',
'OKC':'Oklahoma City Thunder',
'POR':'Portland Trail Blazers',
'UTA':'Utah Jazz'
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
    var obj = {"cmd":"subscribe","topics":["/nba/scoreboard"]};
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
                subscribeToGame("/nba/gametracker/"+gameID+"/ts");
            }
        }
        //else{console.log('no refill');} //data was already present, no refill
        //console.log(nbaGames);

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

