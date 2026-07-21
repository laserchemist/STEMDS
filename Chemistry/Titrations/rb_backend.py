import json
from IPython.display import HTML, display
import random as _r
import ipywidgets as widgets

def reactionbuilder(level, RB_WIDGETS):

    if level not in RB_WIDGETS:

        uid = _r.randint(100000,999999)

        state = widgets.Textarea(
            value="{}",
            layout=widgets.Layout(display="none")
        )

        state.add_class(f"rb-state-{uid}")

        RB_WIDGETS[level] = {
            "uid": uid,
            "state": state
        }


    uid = RB_WIDGETS[level]["uid"]
    state = RB_WIDGETS[level]["state"]


    with open("ReactionBuilder.html", encoding="utf-8") as f:
        html = f.read()


    html = (
        html
        .replace("%%UID%%", str(uid))
        .replace("__LEVEL__", str(level))
    )


    display(state)
    display(HTML(html))

    return state

import json
from IPython.display import HTML, display

import re

def format_ion(ion):
    """
    PO4   -> PO<sub>4</sub>
    NH4   -> NH<sub>4</sub>
    Fe2O3 -> Fe<sub>2</sub>O<sub>3</sub>
    SO4^2- -> SO<sub>4</sub><sup>2-</sup> (optional)
    """

    if not ion:
        return ""

    # numbers become subscripts
    ion = re.sub(r'([A-Za-z])(\d+)', r'\1<sub>\2</sub>', ion)

    # optional: charges become superscripts
    ion = re.sub(r'\^([0-9]*[+-])', r'<sup>\1</sup>', ion)

    return ion

def _mol_html(parts):

    parts = list(parts) + [""] * (5 - len(parts))

    coeff, ion1, sub1, ion2, sub2 = parts[:5]

    html = ""

    if coeff:
        html += f'<span style="color:#1976d2;font-weight:700;">{coeff}</span>'

    html += f'<span style="color:#008000;font-weight:500;">{format_ion(ion1)}</span>'

    if sub1:
        html += f'<span style="color:#FFD700;font-weight:700;"><sub>{sub1}</sub></span>'

    if ion2:

        # Detect polyatomic ions
        polyatomic = len(re.findall(r"[A-Z][a-z]?", ion2)) > 1

        if polyatomic and sub2:
            html += "(" + f'<span style="color:#008000;font-weight:500;">{format_ion(ion2)}</span>' + ")"
        else:
            html += f'<span style="color:#008000;font-weight:500;">{format_ion(ion2)}</span>'

        if sub2:
            html += f'<span style="color:#FFD700;font-weight:700;"><sub>{sub2}</sub></span>'

    return html or "□"

def showreaction(level, RB_WIDGETS):

    if level not in RB_WIDGETS:
        raise KeyError(f"Level {level} has not been created.")

    state = RB_WIDGETS[level]["state"]

    data = json.loads(state.value)

    reactants = data["response"]["reactants"]
    products  = data["response"]["products"]

    left = " + ".join(_mol_html(m) for m in reactants)
    right = " + ".join(_mol_html(m) for m in products)

    display(HTML(f"""
    <div style="
        font-size:30px;
        text-align:center;
        padding:20px;
        font-family:Cambria Math, serif;
    ">
        {left}
        &rarr;
        {right}
    </div>
    """))

import json
import os
import ipywidgets as widgets


def save_rb_state(RB_WIDGETS, path="rb_state.json"):
    data = {}

    for level, obj in RB_WIDGETS.items():
        raw = obj["state"].value
        print("RAW:", level, raw[:50])  # DEBUG

        try:
            parsed = json.loads(raw)
            data[level] = parsed
        except Exception as e:
            print(f"❌ Level {level} failed JSON parse:", e)

    print("FINAL DATA:", data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ wrote file")

def load_rb_state(path="rb_state.json"):
    if not os.path.exists(path):
        print("⚠️ No saved state found")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    RB_WIDGETS = {}

    for level, payload in data.items():

        uid = payload["uid"]

        state = widgets.Textarea(
            value=json.dumps(payload),
            layout=widgets.Layout(display="none")
        )

        state.add_class(f"rb-state-{uid}")

        RB_WIDGETS[int(level)] = {
            "uid": uid,
            "state": state
        }

    print(f"✅ Loaded {len(RB_WIDGETS)} reaction builders")
    return RB_WIDGETS
