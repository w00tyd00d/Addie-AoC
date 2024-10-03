import json
from pathlib import Path


class Cache:

    def __init__(self, year) -> None:
        self.data = {}
        self.file = f'cache/{year}.json'
        self._load_data()

    def set(self, key, val):
        self.data[key] = val

    def get(self, key) -> str:
        if key not in self.data:
            return "Not Found"
        return self.data[key]

    def save_data(self):
        with open(self.file, "w") as f:
            f.write(json.dumps(self.data))

    def _load_data(self):
        if Path(self.file).is_file():
            with open(self.file, "r") as f:
                f_data = f.read()
                if f_data == "":
                    return
                self.data = json.loads(f_data)
