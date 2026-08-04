"""
library.py

Lesson reference library.

Version 0.2
"""

from IPython.display import display
import ipywidgets as widgets
from storage import Storage

REFERENCE_LIBRARY = {}

storage = Storage()

UNLOCKED_LESSONS = storage.load()

class Library:

    def __init__(self):

        self.output = widgets.Output()


    def categories(self):

        result = {}

        for lesson in REFERENCE_LIBRARY.values():

            if lesson.category not in result:
                result[lesson.category] = []

            result[lesson.category].append(
                lesson
            )

        return result


    def show(self):

        children = []

        children.append(
            widgets.HTML(
                "<h2>📚 Reference Library</h2>"
            )
        )


        for category, lessons in self.categories().items():

            children.append(
                widgets.HTML(
                    f"<h3>{category}</h3>"
                )
            )


            for lesson in lessons:

                button = widgets.Button(
                    description=lesson.title
                )


                button.on_click(
                    lambda b, l=lesson: self.open_lesson(l)
                )


                children.append(button)


        children.append(
            self.output
        )
        
        display(
            widgets.VBox(children)
        )



    def open_lesson(self, lesson):

        with self.output:
    
            self.output.clear_output()
    
            lesson.show()

    def get(self, lesson_id):

        return REFERENCE_LIBRARY.get(
            lesson_id
        )

    def is_unlocked(self, lesson_id):

        return lesson_id in UNLOCKED_LESSONS

    def open(self, lesson_id):

        lesson = self.get(lesson_id)
    
        if lesson:
            lesson.show()



UNLOCKED_LESSONS = set()

def unlock(lesson_id):

    UNLOCKED_LESSONS.add(
        lesson_id
    )

    storage.save(
        UNLOCKED_LESSONS
    )