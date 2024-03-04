import json
from pysockets import run as pys_run
import random
from multiprocessing import Process, Queue
from flask import Flask, render_template, g
from teams import teams
app = Flask(__name__)
SB = {}
score_q = Queue()
log_q = Queue()
p = Process(target=pys_run, args=(score_q, log_q))
p.start()


def gen_update():
    val = None
    return {
        "nba": {team: val for team in teams["nba"]},
        "nfl": {team: val for team in teams["nfl"]},
        "mlb": {team: val for team in teams["mlb"]},
        "topics": [],
    }


@app.route('/')
def index():
    global SB
    g.sb = SB
    return render_template('index.html')


@app.route('/new_lines')
def new_lines():
    lines = []
    while not log_q.empty():
        lines.append(log_q.get())
    return lines


@app.route('/new_scores')
def scores():
    global SB
    new_sb = gen_update()
    new_sb.update(SB)
    while not score_q.empty():
        news = score_q.get()
        for league in ["nfl", "nba", "mlb"]:
            new_sb[league].update(news.get(league, {}))
    SB = new_sb
    g.topics = new_sb["topics"]
    return new_sb


def real_score(league, team, new_score):
    new_sb = gen_update()
    new_sb[league][team] = new_score
    return json.dumps(new_sb)


def random_score():
    global SB
    sb = SB
    league = random.choice(list(sb))
    team = random.choice(list(sb[league]))
    score = sb[league][team] or 0
    new_score = score + random.randint(1, 7)
    new_sb = gen_update()
    new_sb[league][team] = new_score
    return json.dumps(new_sb)


portno = None
with open('portno', 'r') as myfile:
    portno = int(myfile.read())
SB = gen_update()
app.run(
    host="0.0.0.0",
    port=portno,
    threaded=True,
)
