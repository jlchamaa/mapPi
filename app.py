from multiprocessing import Process, Queue
from flask import Flask, render_template, g, request
from teams import teams
import pysockets as pys
app = Flask(__name__)
q = Queue()
p = Process(target=pys.run, args=(q,))
p.start()

@app.route('/')
def index():
    g.nba = {team: 0 for team in teams["nba"]}
    g.nfl = {team: 0 for team in teams["nfl"]}
    g.mlb = {team: 0 for team in teams["mlb"]}
    return render_template('index.html')

@app.route('/scoreboard')
def scoreboard():
    return '{"nba": {"BOS": 8}}'


portno=None
with open('portno','r') as myfile:
    portno=int(myfile.read())
app.run(
    host="0.0.0.0",
    port=portno,
    threaded=True,
)
