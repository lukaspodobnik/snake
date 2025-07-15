import json


class HighscoreManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self):
        self._highscores: dict[str, int] = {}

    def update(self, name: str, score: int) -> None:
        self._highscores[name] = score
        self.save()

    def get(self) -> dict[str, int]:
        self.load()
        return self._highscores

    def save(self) -> None:
        with open('save_files/highscore.json', 'w') as f:
            json.dump(self._highscores, f, indent=4)

    def load(self) -> None:
        with open('save_files/highscore.json', 'r') as f:
            self._highscores = json.load(f)
