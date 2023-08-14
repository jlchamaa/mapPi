from multiprocessing import Process, Queue
from flask import Flask, render_template, g, request
import pysockets as pys
app = Flask(__name__)
q = Queue()
p = Process(target=pys.run, args=(q,))
p.start()
sb = {
    "nba": {
        "SEA": 1,
        "DEN": 2,
        "PIT": 3,
    },
    "mlb": {
        "SEA": 1,
        "DEN": 2,
        "PIT": 3,
    },
    "nfl": {
        "SEA": 1,
        "DEN": 2,
        "PIT": 3,
    }
}

@app.route('/')
def index():
    g.nba = sb["nba"]
    g.nfl = sb["nfl"]
    g.mlb = sb["mlb"]
    return render_template('index.html')

@app.route('/scoreboard')
def scoreboard():
    return '{"nba": {"SEA": 8}}'


portno=None
with open('portno','r') as myfile:
    portno=int(myfile.read())
app.run(
    host="0.0.0.0",
    port=portno,
    threaded=True,
)
