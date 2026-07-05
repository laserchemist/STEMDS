
import sys, os
import ipywidgets as widgets

# ── add parent directory so shared files are importable ──────────────────────
# Works whether the notebook is in a lab subdirectory (lab05/) or the root.
# Adds both the current directory and its parent so lab_submit, notebook_style,
# and stemds_quiz are always findable.

cwd = os.getcwd()

paths = [
    cwd,
    os.path.abspath(os.path.join(cwd, "..")),
    os.path.abspath(os.path.join(cwd, "../..")),
]

for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── standard imports ──────────────────────────────────────────────────────────
# ── ensure required packages are installed ───────────────────────────────────
import subprocess as _sp, sys as _sys
def _install(pkg):
    _sp.run(
        [_sys.executable, "-m", "pip", "install", pkg,
         "--quiet", "--break-system-packages"],
        capture_output=True
    )
for _pkg in ["gspread", "google-auth"]:
    _install(_pkg)
print("✅ Required packages ready (gspread, google-auth)")
del _install, _pkg
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
plt.style.use("ggplot")
# Note: %matplotlib inline must be called in the notebook setup cell
import math
import json, glob
import nbformat as nbf
from datascience import *
from gofer.ok import check
from IPython.display import display, HTML
from jupyterquiz import display_quiz
import random as _r

BASE_DIR = os.path.dirname(__file__)
path = os.path.join(BASE_DIR, "CodeBuilder2.html")

# ── styling (from parent directory) ──────────────────────────────────────────
from notebook_style import apply_style
apply_style()

# ── lab version ───────────────────────────────────────────────────────────────
ver = '2026V102'

# ── current notebook path ─────────────────────────────────────────────────────
notebook = max(glob.glob('*.ipynb'), key=os.path.getmtime)

# ── JupyterHub username ───────────────────────────────────────────────────────
user = os.getenv('JUPYTERHUB_USER', 'student')

# ── open-ended answer checker ─────────────────────────────────────────────────
def test_open(text, notebook, length):
    """Check that the markdown cell after the one containing 'text'
    has at least `length` characters."""
    nb_path = max(glob.glob('*.ipynb'), key=os.path.getmtime)
    ntbk = nbf.read(nb_path, nbf.NO_CONVERT)
    for i, cell in enumerate(ntbk.cells):
        if text in cell.source:
            nxt = ntbk.cells[i + 1]
            return 1 if len(nxt.source) >= length else 0
    return 0

# -- ya boi code the builder ---------------------------------------------------

def codebuilder(level, CB_WIDGETS):

    if level not in CB_WIDGETS:

        uid = _r.randint(100000,999999)

        state = widgets.Textarea(
            value="{}",
            layout=widgets.Layout(display="none")
        )

        state.add_class(f"cb-state-{uid}")

        CB_WIDGETS[level] = {
            "uid": uid,
            "state": state
        }

    uid = CB_WIDGETS[level]["uid"]
    state = CB_WIDGETS[level]["state"]

    with open(path, encoding="utf-8") as f:
        html = f.read()

    html = (
        html.replace("%%UID%%", str(uid))
            .replace("__LEVEL__", f"level{level}")
    )

    display(state)
    display(HTML(html))

    return state

def save_cb_state(CB_WIDGETS, path="cb_state.json"):
    data = {}

    for level, obj in CB_WIDGETS.items():
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

def load_cb_state(path="cb_state.json"):
    if not os.path.exists(path):
        print("⚠️ No saved state found")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    CB_WIDGETS = {}

    for level, payload in data.items():
        uid = payload["uid"]

        # IMPORTANT: re-stringify so your JS still works
        state = widgets.Textarea(
            value=json.dumps(payload),
            layout=widgets.Layout(display="none")
        )
        state.add_class(f"cb-state-{uid}")

        CB_WIDGETS[int(level)] = {
            "uid": uid,
            "state": state
        }

    print(f"✅ Loaded {len(CB_WIDGETS)} codebuilders")
    return CB_WIDGETS

def cb_summary(CB_WIDGETS):
    codelist = []
    score = []
    closestTotal = []
    percentage = []
    
    for i in CB_WIDGETS:
        data = json.loads(CB_WIDGETS[i]["state"].value)
        codelist.append(data["response"]["code"])
        score.append(data["evaluation"]["bestMatch"])
        closestTotal.append(data["evaluation"]["bestLength"])
        if data["evaluation"]["bestLength"] > 0:
            percentage.append(data["evaluation"]["bestMatch"]/data["evaluation"]["bestLength"])
        else:
            percentage.append(0)

    
    summary_table = Table().with_columns('number', list(CB_WIDGETS.keys()), 'code', codelist, 'score', score, 'out of', closestTotal, 'percentage', percentage)
    return summary_table

def questions(lab, level):
    with open("Q" + str(lab) + '_' + str(level) + ".json", "r") as file:
        questions=json.load(file)    
    display_quiz(questions)