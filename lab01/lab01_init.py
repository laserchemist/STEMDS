"""
lab01_init.py
=============
Initialization for Lab 01 — all versions.
Students never need to open or edit this file.

Expected directory layout:
    course_root/
    ├── notebook_style.py       ← shared styling
    ├── lab_submit.py           ← shared submission helper
    └── lab01/
        ├── lab01_init.py   ← this file
        ├── lab01_*.ipynb
        ├── questions_01.json (if present)
        └── tests/

In the notebook, the entire setup is just:
    from lab01_init import *
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
get_ipython().run_line_magic("matplotlib", "inline")
plt.style.use("ggplot")
import math
import json, glob
import nbformat as nbf
from datascience import *
from gofer.ok import check
from IPython.display import display
from jupyterquiz import display_quiz

# ── styling (from parent directory) ──────────────────────────────────────────
from notebook_style import apply_style
apply_style()

# ── lab version ───────────────────────────────────────────────────────────────
ver = '2026V101'

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
