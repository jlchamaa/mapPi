import json
from pysockets import run as pys_run
import random
import asyncio
from multiprocessing import Process
from flask import Flask, render_template, g, request
from teams import teams
app = Flask(__name__)
SB = {}

p = Process(target=pys_run)
p.start()


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
    g.topics = ["topic1"]
    return render_template('index.html')

@app.route('/new_lines')
def lines():
    return {"help": "me"}


@app.route('/new_scores')
def scores():
    # new_sb = gen_update()
    # return gen_update()
    return random_score()


def random_score():
    global SB
    sb = SB
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
