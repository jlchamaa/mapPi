
from time import sleep
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, DataTable
from textual.reactive import reactive
from textual.widget import Widget
from datetime import datetime
from teams import teams
import csv
import io

CSV = """lane,swimmer,country,time
4,Joseph Schooling,Singapore,100
2,Michael Phelps,United States,51.14
5,Chad le Clos,South Africa,51.14
6,László Cseh,Hungary,51.14
3,Li Zhuhao,China,51.26
8,Mehdy Metella,France,51.58
7,Tom Shields,United States,51.73
1,Aleksandr Sadovnikov,Russia,51.84"""

class TableApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    reacter = reactive("garbage")

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield ScoreUpdate()

    def on_mount(self) -> None:
        csv_text = ""
        with open('scores.csv', 'r') as file:
            csv_text = file.read()
        # print(csv_text)
        self.table = self.query_one(DataTable)
        rows = csv.reader(io.StringIO(csv_text))
        # rows = csv.reader(io.StringIO(CSV))
        self.table.add_columns(*next(rows))
        self.table.add_rows(rows)
        self.table.add_row("first", self.reacter, "third")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
        self.reacter = "cute"
        self.table.refresh_cell(2,1)

    def watch_reacter(self, older, newer):
        pass

        

class ScoreUpdate(Widget):
    who = reactive("name", layout=True)  
    def render(self) -> str:
        return f"Hello, {self.who}!"

# class Score:
#     def __init__(self, league, team, old_score, new_score, last_updated) -> None:
#         self.league = league
#         self.team = team
#         self.old_score = old_score
#         self.new_score = new_score
#         self.last_updated = last_updated

# def main():
    # old = 0
    # while old < 20:
    #     score = Score("nba", "LAL", old, old+3, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #     print("{} {} {} old={} new={}".format(
    #         score.last_updated,
    #         score.league,
    #         score.team,
    #         score.old_score,
    #         score.new_score,
    #     ))
    #     old += 3
    #     sleep(2)
    # pass


def initialize_csv():
    header = ["last_updated","league","team","old_score","new_score"]
    data = []
    nba = list(teams["nba"].keys())
    nba.sort()
    # print("last_updated,league,team,old_score,new_score")
    for team in nba[0:2]:
        team_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "nba", team, 0, 0]
        data.append(team_data)
        # print("{},nba,{},0,0".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),team))
    with open('scores.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def read_csv():
    with open('scores.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        print(csv_reader)
        # for row in csv_reader:
        #     print(row)

if __name__ == "__main__":
    initialize_csv()


    # read_csv()
    
    # main()

   
    app = TableApp()
    app.run()

    # nba = list(teams["nba"].keys())
    # nba.sort()
    # print("last_updated,league,team,old_score,new_score")
    # for team in nba:
    #     print("{},nba,{},0,0".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),team))