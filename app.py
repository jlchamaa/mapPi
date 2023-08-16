import json
import pysockets as pys
import random
from flask import Flask, render_template, g, request
from multiprocessing import Process, Queue
from teams import teams
app = Flask(__name__)
q = Queue()
p = Process(target=pys.run, args=(q,))
p.start()
SB = {}

def gen_update(start=False):
    val = 0 if start else None
    return {
        "nba": {team: val for team in teams["nba"]},
        "nfl": {team: val for team in teams["nfl"]},
        "mlb": {team: val for team in teams["mlb"]},
    }

@app.route('/')
def index():
    global SB 
    SB = gen_update(start=True)
    g.sb = SB
    return render_template('index.html')

@app.route('/scoreboard')
def scoreboard():
    global SB
    sb = SB
    print(sb)
    league = random.choice(list(sb))
    team = random.choice(list(sb[league]))
    score = sb[league][team] 
    new_score = score + random.randint(1,7)
    new_sb = gen_update()
    new_sb[league][team] = new_score
    return json.dumps(new_sb)

portno=None
with open('portno','r') as myfile:
    portno=int(myfile.read())
app.run(
    host="0.0.0.0",
    port=portno,
    threaded=True,
)
