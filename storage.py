import json
import os


class Storage:

    def __init__(self, filename="database.json"):

        self.filename = filename

    def save(self, data):

        with open(
            self.filename,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    def load(self):

        if not os.path.exists(
            self.filename
        ):

            return {}

        with open(
            self.filename,
            "r"
        ) as file:

            return json.load(file)