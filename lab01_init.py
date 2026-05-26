"""
lab01_init.py
=============
Initialization for Lab 01 — middle school version.
Students never need to open or edit this file.

In the notebook, the entire setup is just:
    from lab01_init import *
"""

# ── imports ───────────────────────────────────────────────────────────────────
import numpy as np
import json, glob, os
import nbformat as nbf
from datascience import *
from gofer.ok import check
from IPython.display import display
from jupyterquiz import display_quiz

# ── styling ───────────────────────────────────────────────────────────────────
from notebook_style import apply_style
apply_style()

# ── lab version (checked by q4_open_ended test) ───────────────────────────────
ver = '2026V101'

# ── current notebook path (needed by test_open) ───────────────────────────────
notebook = max(glob.glob('*.ipynb'), key=os.path.getmtime)

# ── open-ended answer checker ─────────────────────────────────────────────────
def test_open(text, notebook, length):
    """Check that the cell after the one containing 'text' has >= length chars."""
    nb_path = max(glob.glob('*.ipynb'), key=os.path.getmtime)
    ntbk = nbf.read(nb_path, nbf.NO_CONVERT)
    for i, cell in enumerate(ntbk.cells):
        if text in cell.source:
            nxt = ntbk.cells[i + 1]
            return 1 if len(nxt.source) >= length else 0
    return 0
