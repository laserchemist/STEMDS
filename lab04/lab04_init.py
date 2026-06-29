"""
lab04_init.py
=============
Initialization for Lab 04 — Functions.
Students never need to open or edit this file.

Expected layout:
    course_root/
    ├── notebook_style.py
    ├── lab_submit.py
    ├── stemds_quiz.py
    └── lab04/
        ├── lab04_init.py       ← this file
        ├── lab04_*.ipynb
        ├── tests/
        └── EDS_mod/

In the notebook:
    from lab04_init import *
"""

import sys, os

# ── add parent directory so shared files are importable ──────────────────────
_cwd    = os.getcwd()
_parent = os.path.abspath(os.path.join(_cwd, '..'))
for _p in [_cwd, _parent]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

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

# ── standard imports ──────────────────────────────────────────────────────────
import numpy as np
import math
import json, glob
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
plt.style.use("ggplot")
# Note: %matplotlib inline must be called in the notebook setup cell
from datascience import *
from gofer.ok import check
from IPython.display import display

# ── optional imports (silent if not installed) ────────────────────────────────
try:
    from jupyterquiz import display_quiz
except ImportError:
    pass

try:
    from stemds_quiz import open_quiz
except ImportError:
    pass

# ── styling ───────────────────────────────────────────────────────────────────
from notebook_style import apply_style
apply_style()

# ── lab version ───────────────────────────────────────────────────────────────
ver = '2026V104'

# ── current notebook path ─────────────────────────────────────────────────────
notebook = max(glob.glob('*.ipynb'), key=os.path.getmtime)

# ── JupyterHub username ───────────────────────────────────────────────────────
user = os.getenv('JUPYTERHUB_USER', 'student')

# ── open-ended answer checker ─────────────────────────────────────────────────
import nbformat as nbf

def test_open(text, notebook, length):
    """Check that the markdown cell after the one containing 'text'
    has at least 'length' characters."""
    nb_path = max(glob.glob('*.ipynb'), key=os.path.getmtime)
    ntbk = nbf.read(nb_path, nbf.NO_CONVERT)
    for i, cell in enumerate(ntbk.cells):
        if text in cell.source:
            nxt = ntbk.cells[i + 1]
            return 1 if len(nxt.source) >= length else 0
    return 0
