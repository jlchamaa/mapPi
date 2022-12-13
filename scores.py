from textual.app import App
from textual.reactive import reactive
from textual.widget import Widget
from pysockets import ScoreBoard
from teams import teams
sb = ScoreBoard()


class TableApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self):
        yield ScoreUpdate()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
        w = self.query_one(ScoreUpdate)
        w.change_who("cute")

    def watch_reacter(self, older, newer):
        pass


class ScoreUpdate(Widget):
    who = reactive(sb.nba, layout=True)

    def render(self) -> str:
        return f"Hello, {self.who}!"

    def change_who(self, new_who):
        self.who = new_who


if __name__ == "__main__":
    app = TableApp()
    app.run()
