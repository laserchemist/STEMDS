"""
toc_links.py
============
Run this script to regenerate all four TOC notebooks:

    python toc_links.py

Generates:
    TOC.ipynb              — Middle school, full (instructor section included)
    TOC_student.ipynb      — Middle school, student-only
    TOC_hs.ipynb           — High school, full (instructor section included)
    TOC_hs_student.ipynb   — High school, student-only
    TOC_chem.ipynb         — Chem, student-only

All nbgitpuller URL logic and button styling lives here.
TOC notebooks are pure markdown — no code cells, no execution needed.

To add a new notebook:
    Add one line to MS_ACTIVITIES or HS_ACTIVITIES in the format:
    ("filename.ipynb",  "emoji Label",  "Short description"),
"""

import json
from urllib.parse import quote

# ── configuration ─────────────────────────────────────────────────────────────

HUB    = "https://temple.2i2c.cloud"
REPO   = "https://github.com/laserchemist/STEMDS"
BRANCH = "main"
FOLDER = "STEMDS"   # subfolder the repo clones into on the hub

# ══════════════════════════════════════════════════════════════════════════════
#  MIDDLE SCHOOL activities
# ══════════════════════════════════════════════════════════════════════════════
# Each entry: ("filename.ipynb",  "emoji Label",  "Short description")
# ALL THREE fields are required — missing the description crashes at build time.

MS_ACTIVITIES = [
    ("lab00_middle_school.ipynb",
        "🔬 Lab 00",   "Introduction to Data Science"),
    ("lab01_middle_school.ipynb",
        "🔬 Lab 01",   "Introduction to Python as a Tool"),
    ("Activity1_Planetary_Data_Lab.ipynb",
        "🪐 Activity 1", "Planetary Data Lab"),
    ("Activity2_Planet_Builder_Simulator.ipynb",
        "🚀 Activity 2", "Planet Builder Simulator"),
    ("lab02/lab2_middle_school.ipynb",
        "🧮 Lab 02",   "Data types — numbers, strings, arrays"),
    ("lab03/lab3_middle_school.ipynb",
        "🗃️ Lab 03",   "Tables — organising data"),
    ("Lab04-Functions-A.ipynb",
        "⚙️ Lab 04",   "Functions"),
    ("lab05/lab5_middle_school.ipynb",
        "🎲 Lab 05",   "Probability, Simulation & Hypothesis Testing"),
    ("Plant_Explorer.ipynb",
        "🌿 Plant Similarity: Photo Investigation", "Plant Identification"),
    ("Code_Library.ipynb",
        "📖 Your Code Library", "For all your coding needs :)"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  HIGH SCHOOL activities
# ══════════════════════════════════════════════════════════════════════════════

HS_ACTIVITIES = [
    ("lab00_middle_school.ipynb",          # shared with MS — same intro lab
        "🔬 Lab 00",   "Introduction to Data Science"),
    ("lab01_high_school.ipynb",
        "🔬 Lab 01",   "Introduction to Python as a Tool"),
    ("lab02/lab2_high_school.ipynb",
        "🧮 Lab 02",   "Data types — numbers, strings, arrays"),
    ("lab03/lab3_high_school.ipynb",
        "🗃️ Lab 03",   "Tables — organising & analysing data"),
    ("Lab04-Functions-A.ipynb",
        "⚙️ Lab 04",   "Functions"),
    ("lab05/lab5_high_school.ipynb",
        "🎲 Lab 05",   "Probability, Simulation & Hypothesis Testing"),
    ("Plant_Explorer.ipynb",
        "🌿 Plant Similarity: Photo Investigation", "Plant Identification"),
    ("Code_Library.ipynb",
        "📖 Your Code Library", "For all your coding needs :)"),
]

EXERCISES = [
    ("lab01/E1_v1.1.ipynb", "Exercises 01", "Supplemental for Lab 01"),
    ("lab02/E2_v1.3.ipynb", "Exercises 02", "Supplemental for Lab 02"),
    ("lab03/E3_v1.3.ipynb", "Exercises 03", "Supplemental for Lab 03"),
    ("lab04/E4_v1.2.ipynb", "Exercises 04", "Supplemental for Lab 04"),
    ("lab05/E1_v1.5.ipynb", "Exercises 05", "Supplemental for Lab 05")]

REVIEWS = [
    ("lab00/ReviewMaterials/Review_0.ipynb", "Review for Lab 00", "alright beans"),
    ("lab01/ReviewMaterials/Review_1.ipynb", "Review for Lab 01", "cool beans"),
    ("lab02/ReviewMaterials/Review_2.ipynb", "Review for Lab 02", "cooler beans")]

CHEMISTREES = [
    ("Chemistry/CopperPhosphate/Copper Postlab Analysis.ipynb", "Copper Postlab", ":)"),
    ("Chemistry/Density/Density.ipynb", "Density Activity", "Density :)"),
    ("Chemistry/Tea/Caffeine Postlab Analysis.ipynb", "Tea: Caffeine Postlab", "I love caffeine :D"),
    ("Chemistry/Tea/LTheanine Analysis UVvis.ipynb", "Tea: LTheanine UV-vis Postlab", "I love Theanine :D"),
    ("Chemistry/Titrations/Titration Vinegar Postlab.ipynb", "Titration: Vinegar Postlab", "Smells godawful but it's for science I guess"),
    ("Chemistry/Titrations/Titration Sprite Postlab.ipynb", "Titration: Sprite Postlab", "Anyone else fancy a pint of boiled soda?"),
    ("Chemistry/Titrations/Titration Coca Cola Postlab.ipynb", "Titration: Coca-Cola Postlab", "I know I do"),
    ("Chemistry/BestFit/Best Fit.ipynb", "Guide to getting the Best Fit Line", "Expect to use this a lot"),
    ("Chemistry/UnitConvert/UnitConvert.ipynb", "Guide to Unit Conversion", "Unit Conversions :|")]

# ── Instructor-only notebooks (same for both programs) ────────────────────────
# NOTE: security-by-obscurity only — see LOCKING note below.

INSTRUCTOR = [
    ("instructor_dashboard.ipynb",
        "📊 Dashboard", "Instructor Submission Dashboard"),
]

# ── LOCKING note ──────────────────────────────────────────────────────────────
# Students do not receive the full TOC link that shows this section.
# The dashboard only READS submissions.json — no write risk through the UI.
# For stronger protection keep instructor_dashboard.ipynb in a private repo.

# ── colors ────────────────────────────────────────────────────────────────────

CHERRY      = "#9B2335"   # Temple cherry  — middle school buttons
HS_PURPLE   = "#5C2D91"   # Deep violet    — high school buttons
GREY        = "#555555"   # Instructor section (both)
GREEN       = "#06402B"   # green for reviews :)
GOLD        = "#EFBF04"   # gold exercises because they retrieve your memory like a GOlden Retriever haHAHA
LIGHTBLUE  = "#90D5FF"   # light blue because drinking chemicals makes you go into the sky

# ── header HTML ───────────────────────────────────────────────────────────────

def _ms_header():
    return (
        '<img src="Temple_flag_morn.png" alt="Temple University" '
        'style="width:180px;float:right;margin:8px;"/>\n\n'
        '# 🔬 STEM Data Science\n'
        '### Temple University · Summer Program · Middle School\n\n'
        '---'
    )

def _hs_header():
    # Psychedelic gradient banner — vivid, bold, high school energy
    banner = (
        '<div style="'
        'background:linear-gradient(135deg,#1a0033,#6a0080,#c800a0,#ff4060,#ff9900,#ffe000);'
        'border-radius:14px;padding:28px 32px;margin-bottom:18px;'
        'box-shadow:0 4px 24px rgba(200,0,160,0.35);">\n'
        '  <img src="Temple_flag_morn.png" alt="Temple University" '
        'style="width:140px;float:right;margin:0 0 8px 16px;'
        'border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.4);"/>\n'
        '  <span style="font-size:2.2em;font-weight:900;'
        'background:linear-gradient(90deg,#ffe000,#ff9900,#ff4060,#c800a0,#6a0080);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'display:block;line-height:1.2;">⚡ STEM Data Science</span>\n'
        '  <span style="color:#ffffff;font-size:1.15em;font-weight:600;'
        'text-shadow:0 1px 4px rgba(0,0,0,0.5);">'
        'Temple University · Summer Program · High School</span>\n'
        '</div>\n\n---'
    )
    return banner

def _chem_colorz():
    # Some mellower colors, because life is pain
    banner = (
        '<div style="'
        'background:linear-gradient(135deg, #A10100, #DA1F05, #F33C04, #FE650D, #FFC11F, #FFF75D);'
        'border-radius:14px;padding:28px 32px;margin-bottom:18px;'
        'box-shadow:0 4px 24px rgba(200,0,160,0.35);">\n'
        '  <img src="Temple_flag_morn.png" alt="Temple University" '
        'style="width:140px;float:right;margin:0 0 8px 16px;'
        'border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.4);"/>\n'
        '  <span style="font-size:2.2em;font-weight:900;'
        'background:linear-gradient(90deg, #FFF75D, #FFC11F, #FE650D, #F33C04, #DA1F05, #A10100);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'display:block;line-height:1.2;">⚡ STEM-UP Chemistry</span>\n'
        '  <span style="color:#ffffff;font-size:1.15em;font-weight:600;'
        'text-shadow:0 1px 4px rgba(0,0,0,0.5);">'
        'Temple University · Summer Program · High School</span>\n'
        '</div>\n\n---'
    )
    return banner

# ── helpers ───────────────────────────────────────────────────────────────────

def nbgitpuller(filename):
    urlpath = f"tree/{FOLDER}/{filename}"
    return (
        f"{HUB}/hub/user-redirect/git-pull"
        f"?repo={quote(REPO, safe='')}"
        f"&urlpath={quote(urlpath, safe='')}"
        f"&branch={BRANCH}"
    )

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
    for entry in items:
        if len(entry) != 3:
            raise ValueError(
                f"Each entry needs exactly 3 fields "
                f"(filename, label, description).\n"
                f"  Problem entry: {entry}\n"
                f"  Got {len(entry)} field(s) instead of 3."
            )
    return (
        '<div style="margin:12px 0;">\n'
        + "\n".join(button(lbl, desc, nbgitpuller(fname), color)
                    for fname, lbl, desc in items)
        + '\n</div>'
    )

def _resources_section():
    return (
        '## 🔗 Resources\n\n'
        '- [Inferential Thinking — Online Textbook]'
        '(https://inferentialthinking.com/chapters/intro.html)\n'
        '- [Datascience Table Reference](http://data8.org/datascience/index.html)\n'
        '- [Data Science Primer](https://laserchemist.github.io/dprimer/intro.html)\n'
        '- [EDS Course Website](https://sites.temple.edu/data/)'
    )

def _review_section(color=GREEN):
    return '---\n\n## 🧠 Reviews\n\n' + button_group(REVIEWS, color)
def _exercise_section(color=GOLD):
    return '---\n\n## 💪 Exercises\n\n' + button_group(EXERCISES, color)
def _chem_section(color=LIGHTBLUE):
    return '---\n\n## 🧪 Chemistry Postlabs and Activities\n\n' + button_group(CHEMISTREES, color)

def _instructor_section(color=GREY):
    return '---\n\n## 🔒 Instructor\n\n' + button_group(INSTRUCTOR, color)

# ── notebook writer ───────────────────────────────────────────────────────────

def _write_toc(output, header, activities, btn_color, include_reviews, include_exercises, include_chemistry, include_instructor, dark_bg=False):
    sections = [
        header,
        '## 📚 Activities & Labs\n\n'
        '*Click any button to open the notebook on the hub.*\n\n'
        + button_group(activities, btn_color),
        _resources_section(),
    ]
    if include_chemistry:
        sections.append(_chem_section())
    if include_reviews:
        sections.append(_review_section())
    if include_exercises:
        sections.append(_exercise_section())
    if include_instructor:
        sections.append(_instructor_section())

    source = "\n\n".join(sections)

    if dark_bg:
        # Wrap entire content in a dark panel — deep space charcoal,
        # readable against the gradient banner and violet buttons.
        source = (
            '<div style="background:#1a1a2e;color:#e8e8f0;'
            'padding:24px 28px;border-radius:12px;'
            'box-shadow:0 4px 20px rgba(0,0,0,0.5);">\n\n'
            + source
            + '\n\n</div>'
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
            "source": source
        }]
    }

    with open(output, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"  Written → {output}")
    print(f"  Link    → {nbgitpuller(output)}")

# ── public builders ───────────────────────────────────────────────────────────

def build_ms_toc():
    """Middle school — full (with instructor section). Keep link private."""
    print("\n📘 Middle School — Full TOC")
    _write_toc("TOC.ipynb", _ms_header(), MS_ACTIVITIES,
               CHERRY, include_reviews=True, include_exercises=True, include_chemistry=False, include_instructor=True)

def build_ms_toc_student():
    """Middle school — student-only. Share this link freely."""
    print("\n📘 Middle School — Student TOC")
    _write_toc("TOC_student.ipynb", _ms_header(), MS_ACTIVITIES,
               CHERRY, include_reviews=True, include_exercises=True, include_chemistry=False, include_instructor=True)

def build_hs_toc():
    """High school — full (with instructor section). Keep link private."""
    print("\n🔥 High School — Full TOC")
    _write_toc("TOC_hs.ipynb", _hs_header(), HS_ACTIVITIES,
               HS_PURPLE, include_reviews=True, include_exercises=True, include_chemistry=False, include_instructor=True, dark_bg=True)

def build_hs_toc_student():
    """High school — student-only. Share this link freely."""
    print("\n🔥 High School — Student TOC")
    _write_toc("TOC_hs_student.ipynb", _hs_header(), HS_ACTIVITIES,
               HS_PURPLE, include_reviews=True, include_exercises=True, include_chemistry=False, include_instructor=True, dark_bg=True)

def build_toc_chemistry():
    """Chemistry coolthings"""
    print("\n🧪 Chemistry - Student TOC")
    _write_toc("TOC_chem.ipynb", _chem_colorz(), HS_ACTIVITIES, 
               GOLD, include_reviews=True, include_exercises=True, include_chemistry=True, include_instructor=False, dark_bg=False)

# ── run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_ms_toc()
    build_ms_toc_student()
    build_hs_toc()
    build_hs_toc_student()
    build_toc_chemistry()

    print("\n" + "="*60)
    print("SHARE WITH STUDENTS:")
    print("  Middle school → TOC_student.ipynb link above")
    print("  High school   → TOC_hs_student.ipynb link above")
    print("  Chemistry     → TOC_chem.ipynb link above")
    print("\nKEEP PRIVATE (instructor section):")
    print("  Middle school → TOC.ipynb link above")
    print("  High school   → TOC_hs.ipynb link above")
    
