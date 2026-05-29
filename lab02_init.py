"""
lab02_init.py
=============
Initialization for Lab 02 — middle school and high school versions.
Students never need to open or edit this file.

In the notebook, the entire setup is just:
    from lab02_init import *
"""

# ── imports ───────────────────────────────────────────────────────────────────
import numpy as np
import math
import json, glob, os
import nbformat as nbf
from datascience import *
from gofer.ok import check
from IPython.display import display, YouTubeVideo
from jupyterquiz import display_quiz

# ── styling ───────────────────────────────────────────────────────────────────
from notebook_style import apply_style
apply_style()

# ── lab version ───────────────────────────────────────────────────────────────
ver = '2026V102'

# ── current notebook path (needed by open-ended tests) ───────────────────────
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
