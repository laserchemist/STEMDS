"""
toc_links.py
============
Run this script to regenerate TOC.ipynb:

    python toc_links.py

All nbgitpuller URL logic and button styling lives here.
TOC.ipynb is pure markdown — no code cells, no execution needed.

To add a new notebook:
    Add one line to ACTIVITIES in the format:
    ("filename.ipynb",  "emoji Label",  "Short description"),
"""

import json
from urllib.parse import quote

# ── configuration ─────────────────────────────────────────────────────────────

HUB    = "https://temple.2i2c.cloud"
REPO   = "https://github.com/laserchemist/STEMDS"
BRANCH = "main"
FOLDER = "STEMDS"   # subfolder the repo clones into on the hub

# ── Student-facing notebooks ──────────────────────────────────────────────────
# Each entry: ("filename.ipynb",  "emoji Label",  "Short description")
# ALL THREE fields are required — missing the description will crash at build time.

ACTIVITIES = [
    ("lab00_middle_school.ipynb",                "🔬 Lab 00",    "Introduction to Data Science"),
    ("lab01_middle_school.ipynb",                "🔬 Lab 01",    "Introduction to Python as a Tool"),
    ("Activity1_Planetary_Data_Lab.ipynb",       "🪐 Activity 1","Planetary Data Lab"),
    ("Activity2_Planet_Builder_Simulator.ipynb", "🚀 Activity 2","Planet Builder Simulator"),
     ("lab2_middle_school.ipynb", "🧮 Lab 02", "Store data in lists and arrays"),
    ("Lab04-Functions-A.ipynb",                  "🧮 Lab 04",    "Functions"),
("Plant_Explorer.ipynb",                  "🌿Plant Similarity: Photo Investigation",    "Plant Identification"),
    ("Code_Library.ipynb",                       "📖 Your Code Library", "For all your coding needs :)")]

# ── Instructor-only notebooks ─────────────────────────────────────────────────
# These appear in a separate grey section at the bottom of the TOC.
# NOTE: the section is visually separated but not access-restricted —
# anyone with the link can open the dashboard.  Students don't get this
# link; the only protection is obscurity.  See LOCKING note below.

INSTRUCTOR = [
    ("instructor_dashboard.ipynb", "📊 Dashboard", "Instructor Submission Dashboard"),
]

# ── LOCKING note ──────────────────────────────────────────────────────────────
# How "locked" is the instructor section?
#
#   • Students do not receive the TOC nbgitpuller link that shows this section;
#     they get a student-only link (see build_toc_student() below).
#   • Anyone who knows the filename can open the notebook directly, so this is
#     security-by-obscurity only.
#   • The dashboard only READS submissions.json — students can't corrupt data
#     through it because writes require knowing the file path.
#   • For stronger protection, keep instructor_dashboard.ipynb in a separate
#     private repo and never push it to laserchemist/STEMDS.

# ── colors ────────────────────────────────────────────────────────────────────

CHERRY = "#9B2335"   # Temple cherry
GREY   = "#555555"

# ── helpers ───────────────────────────────────────────────────────────────────

def nbgitpuller(filename):
    urlpath = f"lab/tree/{FOLDER}/{filename}"
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
    # Validate tuples before building — catches missing description early
    for entry in items:
        if len(entry) != 3:
            raise ValueError(
                f"Each ACTIVITIES entry needs exactly 3 fields "
                f"(filename, label, description).\n"
                f"  Problem entry: {entry}\n"
                f"  Got {len(entry)} field(s) instead of 3."
            )
    return ('<div style="margin:12px 0;">\n' +
            "\n".join(button(l, d, nbgitpuller(f), color) for f, l, d in items) +
            '\n</div>')

# ── build full TOC (instructor + students) ────────────────────────────────────

def build_toc(output="TOC.ipynb"):
    """Full TOC with instructor section — keep this link private."""
    _write_toc(output, include_instructor=True)
    print(f"\n📎 Share with STUDENTS (no instructor section):")
    print(f"   python toc_links.py  → use TOC_student.ipynb link instead")
    print(f"\n🔒 Instructor link (keep private):")
    print(f"   {nbgitpuller(output)}")

# ── build student-only TOC ────────────────────────────────────────────────────

def build_toc_student(output="TOC_student.ipynb"):
    """Student TOC — no instructor section. Share this link freely."""
    _write_toc(output, include_instructor=False)
    print(f"\n📎 Share this link with students:")
    print(f"   {nbgitpuller(output)}")

# ── internal writer ───────────────────────────────────────────────────────────

def _write_toc(output, include_instructor=True):
    sections = [
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
         '- [Inferential Thinking — Online Textbook]'
         '(https://inferentialthinking.com/chapters/intro.html)\n'
         '- [Datascience Table Reference](http://data8.org/datascience/index.html)\n'
         '- [Data Science Primer](https://laserchemist.github.io/dprimer/intro.html)\n'
         '- [EDS Course Website](https://sites.temple.edu/data/)'),
    ]

    if include_instructor:
        sections.append(
            '---\n\n## 🔒 Instructor\n\n' +
            button_group(INSTRUCTOR, GREY)
        )

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3 (ipykernel)",
                           "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.3"}
        },
        "cells": [{
            "cell_type": "markdown",
            "id": "toc-main",
            "metadata": {},
            "source": "\n\n".join(sections)
        }]
    }

    with open(output, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"Written → {output}")

# ── run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_toc()
    build_toc_student()
