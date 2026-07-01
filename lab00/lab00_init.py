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
        ├── lab00_init.py   ← this file
        ├── lab00_*.ipynb
        ├── questions_00.json (if present)
        └── tests/

In the notebook, the entire setup is just:
    from lab01_init import *
"""

import sys, os

# ── add parent directory so shared files are importable ──────────────────────
# Works whether the notebook is in a lab subdirectory (lab05/) or the root.
# Adds both the current directory and its parent so lab_submit, notebook_style,
# and stemds_quiz are always findable.
_cwd = os.getcwd()
_parent = os.path.abspath(os.path.join(_cwd, '..'))
for _p in [_cwd, _parent]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

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
from IPython.display import display
from jupyterquiz import display_quiz

# ── styling (from parent directory) ──────────────────────────────────────────
from notebook_style import apply_style
apply_style()

# ── lab version ───────────────────────────────────────────────────────────────
ver = '2026V100'

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
