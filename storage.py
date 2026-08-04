"""
storage.py

Handles saving/loading user progress.

Version 0.1
"""

import json
import os


PROGRESS_FILE = "lesson_progress.json"


class Storage:


    def save(self, unlocked_lessons):

        data = {
            "unlocked_lessons": list(unlocked_lessons)
        }


        with open(
            PROGRESS_FILE,
            "w"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )



    def load(self):

        if not os.path.exists(
            PROGRESS_FILE
        ):

            return set()


        with open(
            PROGRESS_FILE,
            "r"
        ) as f:

            data = json.load(f)


        return set(
            data.get(
                "unlocked_lessons",
                []
            )
        )