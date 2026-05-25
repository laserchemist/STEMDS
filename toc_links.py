"""
toc_links.py
============
Run this script to regenerate TOC.ipynb:

    python toc_links.py

All nbgitpuller URL logic and button styling lives here.
TOC.ipynb is pure markdown — no code cells, no execution needed.
"""

import json
from urllib.parse import quote

# ── configuration ─────────────────────────────────────────────────────────────

HUB    = "https://temple.2i2c.cloud"
REPO   = "https://github.com/laserchemist/STEMDS"
BRANCH = "main"
FOLDER = "STEMDS"          # subfolder the repo clones into on the hub

# Student-facing notebooks — (filename, button label, description)
ACTIVITIES = [
    ("lab00_middle_school.ipynb",               "🔬 Lab 00",    "Introduction to Data Science"),
    ("Activity1_Planetary_Data_Lab.ipynb",      "🪐 Activity 1","Planetary Data Lab"),
    ("Activity2_Planet_Builder_Simulator.ipynb","🚀 Activity 2","Planet Builder Simulator"),
    ("Lab04-Functions-A.ipynb",                 "🧮 Lab 04",    "Functions"),
]

# Instructor-only notebooks
INSTRUCTOR = [
    ("instructor_dashboard.ipynb", "📊 Dashboard", "Instructor Submission Dashboard"),
]

# ── colors ────────────────────────────────────────────────────────────────────

CHERRY = "#9B2335"   # Temple cherry
GREY   = "#555555"

# ── helpers ───────────────────────────────────────────────────────────────────

def nbgitpuller(filename):
    urlpath = f"tree/{FOLDER}/{filename}"
    return (f"{HUB}/hub/user-redirect/git-pull"
            f"?repo={quote(REPO, safe='')}"
            f"&urlpath={quote(urlpath, safe='')}"
            f"&branch={BRANCH}")

def button(label, desc, url, color):
    return (
        f'<a href="{url}" target="_blank" style="text-decoration:none;">\n'
        f'  <div style="background:{color};color:white;border-radius:10px;'
        f'padding:16px 24px;margin:8px 4px;display:inline-block;'
        f'min-width:340px;max-width:420px;vertical-align:top;'
        f'box-shadow:2px 2px 6px rgba(0,0,0,0.18);">\n'
        f'    <span style="font-size:1.25em;font-weight:700;">{label}</span><br>\n'
        f'    <span style="font-size:1.0em;opacity:0.92;">{desc}</span>\n'
        f'  </div>\n'
        f'</a>'
    )

def button_group(items, color):
    return '<div style="margin:12px 0;">\n' + \
           "\n".join(button(l, d, nbgitpuller(f), color) for f, l, d in items) + \
           '\n</div>'

# ── build notebook ────────────────────────────────────────────────────────────

def build_toc(output="TOC.ipynb"):
    markdown = "\n\n".join([
        # header
        ('<img src="Temple_flag_morn.png" alt="Temple University" '
         'style="width:180px;float:right;margin:8px;"/>\n\n'
         '# STEM Data Science\n'
         '### Temple University · Summer Program\n\n'
         '---'),

        # activities
        ('## 📚 Activities & Labs\n\n'
         '*Click any button to open the notebook on the hub.*\n\n'
         + button_group(ACTIVITIES, CHERRY)),

        # resources
        ('## 🔗 Resources\n\n'
         '- [Inferential Thinking — Online Textbook](https://inferentialthinking.com/chapters/intro.html)\n'
         '- [Datascience Table Reference](http://data8.org/datascience/index.html)\n'
         '- [Data Science Primer](https://laserchemist.github.io/dprimer/intro.html)\n'
         '- [EDS Course Website](https://sites.temple.edu/data/)'),

        # instructor
        ('---\n\n'
         '## 🔒 Instructor\n\n'
         + button_group(INSTRUCTOR, GREY)),
    ])

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (ipykernel)",
                           "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.3"}
        },
        "cells": [
            {
                "cell_type": "markdown",
                "id": "toc-main",
                "metadata": {},
                "source": markdown
            }
        ]
    }

    with open(output, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"Written → {output}")
    print(f"\nnbgitpuller link for this TOC:")
    print(nbgitpuller("TOC.ipynb"))

if __name__ == "__main__":
    build_toc()
