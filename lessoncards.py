"""
lessoncards.py

Interactive lesson card framework.

Version 1.0
"""

from IPython.display import display, HTML
import uuid
import json
import html
import base64
import mimetypes
from library import *
import re
import textwrap
from pathlib import Path



# ============================================================
# Basic Content Elements
# ============================================================

class Element:

    def render(self):
        return ""



class Heading(Element):

    def __init__(self, text):
        self.text = text


    def render(self):

        escaped = html.escape(self.text)
    
        # Bold: **text**
        escaped = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
            escaped
        )
    
        # Italics: *text*
        escaped = re.sub(
            r"\*(.*?)\*",
            r"<em>\1</em>",
            escaped
        )
    
        # Inline code: `text`
        escaped = re.sub(
            r"`(.*?)`",
            r"<code>\1</code>",
            escaped
        )
    
        escaped = escaped.replace(
            "\n",
            "<br>"
        )

        return f"""
        <h2 class="card-heading">
            {escaped}
        </h2>
        """


class Text(Element):

    def __init__(self, text):
        self.text = text


    def render(self):

        escaped = html.escape(self.text)
    
        # Bold: **text**
        escaped = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
            escaped
        )
    
        # Italics: *text*
        escaped = re.sub(
            r"\*(.*?)\*",
            r"<em>\1</em>",
            escaped
        )
    
        # Inline code: `text`
        escaped = re.sub(
            r"`(.*?)`",
            r"<code>\1</code>",
            escaped
        )
    
        escaped = escaped.replace(
            "\n",
            "<br>"
        )
    
        return f"""
        <div class="card-text">
            {escaped}
        </div>
        """

class Note(Element):

    def __init__(self, text):
        self.text = text


    def render(self):

        escaped = html.escape(self.text)
    
        # Bold: **text**
        escaped = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
            escaped
        )
    
        # Italics: *text*
        escaped = re.sub(
            r"\*(.*?)\*",
            r"<em>\1</em>",
            escaped
        )
    
        # Inline code: `text`
        escaped = re.sub(
            r"`(.*?)`",
            r"<code>\1</code>",
            escaped
        )
    
        escaped = escaped.replace(
            "\n",
            "<br>"
        )

        return f"""

        <div class="note-box">

            <div class="note-title">

                💡 Note

            </div>


            <div class="note-content">

                {escaped}

            </div>

        </div>

        """

class Warning(Element):

    def __init__(self, text):
        self.text = text


    def render(self):

        escaped = html.escape(self.text)
    
        # Bold: **text**
        escaped = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
            escaped
        )
    
        # Italics: *text*
        escaped = re.sub(
            r"\*(.*?)\*",
            r"<em>\1</em>",
            escaped
        )
    
        # Inline code: `text`
        escaped = re.sub(
            r"`(.*?)`",
            r"<code>\1</code>",
            escaped
        )
    
        escaped = escaped.replace(
            "\n",
            "<br>"
        )

        return f"""

        <div class="warning-box">

            <div class="warning-title">

                ⚠ Warning

            </div>


            <div class="warning-content">

                {escaped}

            </div>

        </div>

        """

class Example(Element):

    def __init__(self, text):
        self.text = text


    def render(self):

        escaped = html.escape(self.text)

        escaped = escaped.replace(
            "\n",
            "<br>"
        )

        return f"""

        <div class="example-box">

            <div class="example-title">

                🔎 Example

            </div>


            <div class="example-content">

                {escaped}

            </div>

        </div>

        """


class Image(Element):

    def __init__(self, path, width=None):

        self.path = path
        self.width = width


    def render(self):

        base = Path(__file__).parent
        image_path = (
            Path(__file__).parent
            / "LC_images"
            / self.path
        )

        with open(image_path, "rb") as f:

            data = base64.b64encode(
                f.read()
            ).decode()

        mime, _ = mimetypes.guess_type(image_path)

        if mime is None:
            mime = "image/png"

        if self.width is None:
            size = ""

        else:
            size = f"width:{self.width}px;"

        return f"""
        <div class="image-wrapper">

            <img
            src="data:{mime};base64,{data}"
            style="{size}"
            class="card-image">

        </div>
        """

class Row(Element):

    def __init__(self, *elements, widths=None):

        self.elements = elements
        self.widths = widths


    def render(self):

        content = ""


        for i, element in enumerate(self.elements):

            if self.widths:

                width = self.widths[i]

                style = (
                    f"flex:{width};"
                )

            else:

                style = ""


            content += f"""

            <div class="row-item"
            style="{style}">

                {element.render()}

            </div>

            """


        return f"""

        <div class="card-row">

            {content}

        </div>

        """

class Column(Element):

    def __init__(self, *elements):

        self.elements = elements


    def render(self):

        content = ""

        for element in self.elements:

            content += element.render()


        return f"""

        <div class="card-column">

            {content}

        </div>

        """


class Code(Element):

    def __init__(self, code):
        self.code = code


    def render(self):

        code_id = (
            "code_"
            +
            str(uuid.uuid4())
            .replace("-", "")
        )

        escaped = html.escape(self.code)

        escaped = html.escape(
            textwrap.dedent(self.code).strip()
        )

        return f"""

        <div class="code-wrapper">

            <button
                class="copy-button"
                onclick="copyCode('{code_id}')">
        
                📋
        
            </button>
        
            <pre id="{code_id}" class="code-block">{escaped}</pre>
        
        </div>

        """

class BulletList(Element):

    def __init__(self, *items):
        self.items = items

    def render(self):

        html_items = ""

        for item in self.items:

            html_items += f"<li>{html.escape(item)}</li>"

        return f"""
        <ul class="card-list">
            {html_items}
        </ul>
        """

class Lesson:

    def __init__(
        self,
        id,
        title,
        category,
        cards,
        description=""
    ):

        self.id = id
        self.title = title
        self.category = category
        self.cards = cards
        self.description = description

        REFERENCE_LIBRARY[id] = self


    def show(self):

        unlock(self.id)

        LessonCards(
            self.title,
            self.cards
        ).show()

# ============================================================
# Card Object
# ============================================================

class Card:

    def __init__(self, *elements):

        self.elements = elements


    def render(self):

        content = ""

        for element in self.elements:
            content += element.render()

        return content



# ============================================================
# Lesson Object
# ============================================================

class LessonCards:


    def __init__(self, title, cards):

        self.title = title
        self.cards = cards
        self.id = "lesson_" + str(uuid.uuid4()).replace("-", "")



    def show(self):
    
        """
        Display the interactive lesson with side navigation.
        """
    
        card_contents = [
    
            card.render()
    
            for card in self.cards
    
        ]
    
    
        data = json.dumps(card_contents)
    
    
    
        html = f"""
    
        <div id="{self.id}" class="lesson-wrapper">
    
    
            <div class="lesson-title">
    
                {self.title}
    
            </div>
    
    
            <div class="lesson-main">
    
    
                <button class="nav-button left"
    
                    onclick="prev_{self.id}()">
    
                    ◀
    
                </button>
    
    
    
                <div class="lesson-card"
    
                    id="{self.id}_content">
    
                </div>
    
    
    
                <button class="nav-button right"
    
                    onclick="next_{self.id}()">
    
                    ▶
    
                </button>
    
    
            </div>
    
    
    
            <div class="lesson-progress"
    
                id="{self.id}_counter">
    
            </div>
    
    
    
        </div>
    
    
    
        <style>

        .note-box {{

            margin-top:20px;
        
            padding:15px;
        
            border-radius:10px;
        
            border-left:6px solid #888888;
        
            background:#f5f5f5;
        
        }}
        
        
        
        .note-title {{
        
            font-weight:bold;
        
            margin-bottom:8px;
        
        }}
        
        
        
        .note-content {{
        
            line-height:1.5;
        
        }}

        .warning-box {{
        
            margin-top:20px;
        
            padding:15px;
        
            border-radius:10px;
        
            border-left:6px solid #999999;
        
            background:#fafafa;
        
        }}
        
        
        
        .warning-title {{
        
            font-weight:bold;
        
            margin-bottom:8px;
        
        }}
        
        
        
        .warning-content {{
        
            line-height:1.5;
        
        }}

        .example-box {{

            margin-top:20px;
        
            padding:15px;
        
            border-radius:10px;
        
            border-left:6px solid #888888;
        
            background:#f8f8f8;
        
        }}
        
        
        
        .example-title {{
        
            font-weight:bold;
        
            margin-bottom:8px;
        
        }}
        
        
        
        .example-content {{
        
            line-height:1.5;
        
        }}

        .image-wrapper {{

            margin-top:20px;
        
            margin-bottom:20px;
        
            text-align:center;
        
        }}

        .card-list {{

            margin-top: 15px;
        
            margin-bottom: 15px;
        
            line-height: 1.6;
        
        }}
                
        
        
        .card-image {{
        
            max-width:100%;
        
            border-radius:10px;
        
        }}

        .card-row {{

            display:flex;
        
            align-items:center;
        
            gap:25px;
        
            margin-top:20px;
        
            margin-bottom:20px;
        
        }}
        
        
        
        .row-item {{
        
            min-width:0;
        
        }}

        .card-column {{

            display:flex;
        
            flex-direction:column;
        
            gap:15px;
        
        }}
    
    
        .lesson-wrapper {{
    
            width:900px;
            margin:auto;
    
            font-family:
            Arial, sans-serif;
    
        }}
    
    
    
        .lesson-title {{
    
            font-size:28px;
            font-weight:bold;
    
            text-align:center;
    
            margin-bottom:20px;
    
        }}
    
    
    
        .lesson-main {{
    
            display:flex;
    
            align-items:center;
    
            justify-content:center;
    
            gap:25px;
    
        }}
    
    
    
        .lesson-card {{
    
            width:650px;
    
            min-height:300px;
    
            border:
            1px solid #cccccc;
    
            border-radius:14px;
    
            padding:30px;
    
            box-shadow:
            0px 3px 8px rgba(0,0,0,0.15);
    
        }}
    
    
    
        .nav-button {{
    
            width:45px;
    
            height:70px;
    
            border-radius:10px;
    
            border:
            1px solid #aaaaaa;
    
            background:white;
    
            font-size:25px;
    
            cursor:pointer;
    
        }}
    
    
    
        .nav-button:hover {{
    
            background:#eeeeee;
    
        }}
    
    
    
        .lesson-progress {{
    
            text-align:center;
    
            margin-top:20px;
    
            color:#666666;
    
            font-size:15px;
    
        }}

        .code-wrapper {{

            position: relative;
        
            margin-top: 20px;
        
            margin-bottom: 20px;
        
        }}
        
        
        .copy-button {{
        
            position: absolute;
        
            top: 8px;
        
            right: 8px;
        
            border: none;
        
            background: transparent;
        
            cursor: pointer;
        
            font-size: 18px;
        
            opacity: 0.6;
        
        }}
        
        .copy-button:hover {{
        
            opacity: 1;
        
        }}
        
        
        
        .code-block {{
        
            background: #f2f2f2;
        
            border: 1px solid #dddddd;
        
            border-radius: 8px;
        
            padding: 18px;
        
            overflow-x: auto;
        
            font-family: "Courier New", monospace;
        
            font-size: 14px;
        
        }}
    
    
        </style>
    
    
    
        <script type="text/javascript">

        function copyCode(id){{

            navigator.clipboard.writeText(
                document
                .getElementById(id)
                .innerText
                .trim()
            );
        
        }}
    
        let cards_{self.id} = {data};
    
    
        let current_{self.id}=0;

    
        function update_{self.id}(){{
    
    
            document.getElementById(
                "{self.id}_content"
            ).innerHTML =
    
            cards_{self.id}[current_{self.id}];
    
    
    
            let dots="";
    
    
    
            for(
                let i=0;
                i<cards_{self.id}.length;
                i++
            ){{
    
    
                if(i===current_{self.id}){{
    
                    dots += "● ";
    
                }}
    
                else{{
    
                    dots += "○ ";
    
                }}
    
            }}
    
    
    
            document.getElementById(
                "{self.id}_counter"
            ).innerHTML =
            
            dots +
            "<br>Card " +
            String(current_{self.id}+1) +
            " / " +
            String(cards_{self.id}.length);
    
    
    
        }}
    
    
    
        function next_{self.id}(){{
    
    
            if(
                current_{self.id}
                <
                cards_{self.id}.length-1
            ){{
    
    
                current_{self.id}++;
    
                update_{self.id}();
    
    
            }}
    
    
        }}
    
    
    
        function prev_{self.id}(){{
    
    
            if(
                current_{self.id}
                >
                0
            ){{
    
    
                current_{self.id}--;
    
                update_{self.id}();
    
    
            }}
    
        }}
    
    
    
        document.addEventListener(
    
            "keydown",
    
            function(event){{
    
    
                if(event.key==="ArrowRight"){{
    
                    next_{self.id}();
    
                }}
    
    
    
                if(event.key==="ArrowLeft"){{
    
                    prev_{self.id}();
    
                }}
    
    
            }}
    
        );
    
    
    
        update_{self.id}();
    
    
        </script>
    
    
        """
    
        display(HTML(html))

# ============================================================
# Convenience Function
# ============================================================

def lesson(
    id,
    title,
    category,
    cards
):
    return Lesson(
        id,
        title,
        category,
        cards
    )