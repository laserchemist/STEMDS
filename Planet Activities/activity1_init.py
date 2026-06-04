"""
activity1_init.py
=================
Initialization for Activity 1 — The Martian Data Lab (all versions).
Students never need to open or edit this file.

Expected directory layout:
    course_root/
    ├── notebook_style.py               ← shared styling
    ├── lab_submit.py                   ← shared submission helper
    └── activity1/
        ├── activity1_init.py           ← this file
        ├── Activity1_Planetary_Data_Lab.ipynb
        ├── questions_exoplanets.json   ← JupyterQuiz questions
        └── tests/

In the notebook, the entire setup is just:
    from activity1_init import *
"""

import sys, os

# ── add parent directory so shared files are importable ──────────────────────
_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

# ── standard imports ──────────────────────────────────────────────────────────
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
get_ipython().run_line_magic("matplotlib", "inline")
plt.rcParams.update({'figure.dpi': 110, 'font.size': 11})
import math
import json, glob
import nbformat as nbf
from datascience import *
from IPython.display import display
from jupyterquiz import display_quiz

# ── styling (from parent directory) ──────────────────────────────────────────
try:
    from notebook_style import apply_style
    apply_style()
except ImportError:
    pass   # styling is optional; notebook still runs without it

# ── activity version ──────────────────────────────────────────────────────────
ver = '2026V101'

# ── current notebook path ─────────────────────────────────────────────────────
notebook = max(glob.glob('*.ipynb'), key=os.path.getmtime)

# ── JupyterHub username ───────────────────────────────────────────────────────
user = os.getenv('JUPYTERHUB_USER', 'student')

# ── Goldilocks / habitability helper (used by multiple cells) ─────────────────
def habitability_score(temp_c, is_rocky, water_status):
    """
    Return a habitability score from 0–10 based on:
      • Temperature (up to 5 pts) — optimal near 20 °C
      • Rocky surface bonus (2 pts)
      • Water presence bonus (up to 3 pts)
    """
    score = 0

    # Temperature scoring (up to 5 points)
    if -20 <= temp_c <= 60:
        temp_score = 5 - abs(temp_c - 20) / 16   # peaks at ~20 °C
        score += max(0, temp_score)
    elif -60 <= temp_c < -20 or 60 < temp_c <= 100:
        score += 1   # marginal

    # Rocky bonus
    if is_rocky:
        score += 2

    # Water bonus
    water_bonus = {'Yes': 3, 'Possibly': 2, 'Unknown': 1, 'No': 0}
    score += water_bonus.get(water_status, 0)

    return round(min(score, 10), 2)

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

print(f"✅ Activity 1 initialized — version {ver}  |  user: {user}")
print("🚀 Ready for planetary exploration!")
