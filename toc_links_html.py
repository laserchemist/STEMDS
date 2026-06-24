"""
toc_links_html.py
=================
Run this script to regenerate all five TOC HTML landing pages:

    python toc_links_html.py

Generates:
    TOC.html              — Middle school, full (instructor section included)
    TOC_student.html      — Middle school, student-only
    TOC_hs.html           — High school, full (instructor section included)
    TOC_hs_student.html   — High school, student-only
    TOC_chem.html         — Chem, student-only

Why HTML instead of .ipynb?
    nbgitpuller performs a "theirs" merge on notebooks, which can leave
    the hub copy stale when cells have been run or re-ordered.  Plain
    HTML files have no cell metadata, so they are always cleanly
    overwritten on every pull — the landing page is always up-to-date.

    Open any of these files in JupyterLab via File > Open from Path,
    or link directly to them with an nbgitpuller URL using urlpath=
    lab/tree/STEMDS/TOC_student.html  (JupyterLab renders HTML inline).

To add a new notebook:
    Add one line to MS_ACTIVITIES or HS_ACTIVITIES in the format:
    ("filename.ipynb",  "emoji Label",  "Short description"),
"""

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
    ("lab00/lab00_middle_school.ipynb",
        "🔬 Lab 00",   "Introduction to Data Science"),
    ("lab01/lab01_middle_school.ipynb",
        "🔬 Lab 01",   "Introduction to Python as a Tool"),
    ("Planet Activities/Activity1_Planetary_Data_Lab.ipynb",
        "🪐 Activity 1", "Planetary Data Lab"),
    ("Planet Activities/Activity2_Planet_Builder_Simulator.ipynb",
        "🚀 Activity 2", "Planet Builder Simulator"),
    ("lab02/lab02_middle_school.ipynb",
        "🧮 Lab 02",   "Data types — numbers, strings, arrays"),
    ("lab03/lab03_middle_school.ipynb",
        "🗃️ Lab 03",   "Tables — organising data"),
    ("lab04/lab04_middle_school.ipynb",
        "⚙️ Lab 04",   "Functions"),
    ("lab05/lab05_middle_school.ipynb",
        "🎲 Lab 05",   "Probability, Simulation & Hypothesis Testing"),
    ("Plant Activity/Plant_Explorer.ipynb",
        "🌿 Plant Similarity: Photo Investigation", "Plant Identification"),
    ("Code Library/Code_Library.ipynb",
        "📖 Your Code Library", "For all your coding needs :)"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  HIGH SCHOOL activities
# ══════════════════════════════════════════════════════════════════════════════

HS_ACTIVITIES = [
    ("lab00/lab00_high_school.ipynb",
        "🔬 Lab 00",   "Introduction to Data Science"),
    ("lab01/lab01_high_school.ipynb",
        "🔬 Lab 01",   "Introduction to Python as a Tool"),
    ("lab02/lab02_high_school.ipynb",
        "🧮 Lab 02",   "Data types — numbers, strings, arrays"),
    ("lab03/lab03_high_school.ipynb",
        "🗃️ Lab 03",   "Tables — organising & analysing data"),
    ("lab04/lab04_high_school.ipynb",
        "⚙️ Lab 04",   "Functions"),
    ("lab05/lab05_high_school.ipynb",
        "🎲 Lab 05",   "Probability, Simulation & Hypothesis Testing"),
    ("Plant Activity/Plant_Explorer.ipynb",
        "🌿 Plant Similarity: Photo Investigation", "Plant Identification"),
    ("Hypothesis_Test/Hypothesis_Test.ipynb",
        "Hypothesis Test Activity", "Guide to doing the P-test"),
    ("Code Library/Code_Library.ipynb",
        "📖 Your Code Library", "For all your coding needs :)"),
]

EXERCISES = [
    ("lab01/E1_v1.1.ipynb", "Exercises 01", "Supplemental for Lab 01"),
    ("lab02/E2_v1.3.ipynb", "Exercises 02", "Supplemental for Lab 02"),
    ("lab03/E3_v1.3.ipynb", "Exercises 03", "Supplemental for Lab 03"),
    ("lab04/E4_v1.2.ipynb", "Exercises 04", "Supplemental for Lab 04"),
    ("lab05/E1_v1.5.ipynb", "Exercises 05", "Supplemental for Lab 05"),
]

REVIEWS = [
    ("lab00/ReviewMaterials/Review_0.ipynb", "Review for Lab 00", "alright beans"),
    ("lab01/ReviewMaterials/Review_1.ipynb", "Review for Lab 01", "cool beans"),
    ("lab02/ReviewMaterials/Review_2.ipynb", "Review for Lab 02", "cooler beans"),
]

CHEMISTREES = [
    ("Chemistry/CopperPhosphate/Copper Postlab Analysis.ipynb", "Copper Postlab", ":)"),
    ("Chemistry/Density/Density.ipynb", "Density Activity", "Density :)"),
    ("Chemistry/Tea/Caffeine Postlab Analysis.ipynb", "Tea: Caffeine Postlab", "I love caffeine :D"),
    ("Chemistry/Tea/LTheanine Analysis UVvis.ipynb", "Tea: LTheanine UV-vis Postlab", "I love Theanine :D"),
    ("Chemistry/Titrations/Titration Vinegar Postlab.ipynb", "Titration: Vinegar Postlab", "Smells godawful but it's for science I guess"),
    ("Chemistry/Titrations/Titration Sprite Postlab.ipynb", "Titration: Sprite Postlab", "Anyone else fancy a pint of boiled soda?"),
    ("Chemistry/Titrations/Titration Coca Cola Postlab.ipynb", "Titration: Coca-Cola Postlab", "I know I do"),
    ("Chemistry/GasLaw/PvV.ipynb", "Pressure vs. Volume Activity", "Gas Law Experiment 1"),
    ("Chemistry/GasLaw/PvN.ipynb", "Pressure vs. Number of Molecules Activity", "Gas Law Experiment 2"),
    ("Chemistry/GasLaw/PvT.ipynb", "Pressure vs. Temperature Activity", "Gas Law Experiment 3"),
    ("Chemistry/UnitConvert/UnitConvert.ipynb", "Guide to Unit Conversion", "Unit Conversions :|")
]

GROUP_PROJ = [
    ("Group-Project/Group_Project_Datasets.ipynb", "View Datasets", "I love numberz"),
    ("Group-Project/GroupProject_Submission.ipynb", "Submit Group Choice", "No refunds lol"),
    ("Group-Project/GroupProject_Dashboard.ipynb", "View Groups", "In case you forgot"),
    ("Group-Project/example_group_project-indego_bikes/Indego.ipynb", "Example Final Project", "For your reference")
]

# ── Instructor-only notebooks ─────────────────────────────────────────────────
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

CHERRY    = "#9B2335"   # Temple cherry  — middle school buttons
HS_PURPLE = "#5C2D91"   # Deep violet    — high school buttons
GREY      = "#555555"   # Instructor section (both)
GREEN     = "#06402B"   # green for reviews
GOLD      = "#EFBF04"   # gold exercises
LIGHTBLUE = "#90D5FF"   # light blue for chemistry
CRIMSON   = "#990000"   # blood for final proj

# ── URL helpers ───────────────────────────────────────────────────────────────

def toc_linker(filename):
    """nbgitpuller URL that opens the file in classic Notebook view."""
    urlpath = f"tree/{FOLDER}/{filename}"
    return (
        f"{HUB}/hub/user-redirect/git-pull"
        f"?repo={quote(REPO, safe='')}"
        f"&urlpath={quote(urlpath, safe='')}"
        f"&branch={BRANCH}"
    )

def nbgitpuller(filename):
    """nbgitpuller URL that opens the file in JupyterLab."""
    urlpath = f"lab/tree/{FOLDER}/{filename}"
    return (
        f"{HUB}/hub/user-redirect/git-pull"
        f"?repo={quote(REPO, safe='')}"
        f"&urlpath={quote(urlpath, safe='')}"
        f"&branch={BRANCH}"
    )

# ── HTML component builders ───────────────────────────────────────────────────

def _button_html(label, desc, url, color, text_color):
    return (
        f'<a href="{url}" target="_blank" style="text-decoration:none;">'
        f'<div style="background:{color};color:{text_color};border-radius:10px;'
        f'padding:16px 24px;margin:8px 4px;display:inline-block;'
        f'min-width:340px;max-width:420px;vertical-align:top;'
        f'box-shadow:2px 2px 6px rgba(0,0,0,0.18);">'
        f'<span style="font-size:1.25em;font-weight:700;">{label}</span><br>'
        f'<span style="font-size:1.0em;opacity:0.92;">{desc}</span>'
        f'</div></a>'
    )

def _button_group_html(items, color, text_color):
    for entry in items:
        if len(entry) != 3:
            raise ValueError(
                f"Each entry needs exactly 3 fields "
                f"(filename, label, description).\n"
                f"  Problem entry: {entry}\n"
                f"  Got {len(entry)} field(s) instead of 3."
            )
    buttons = "\n".join(
        _button_html(lbl, desc, nbgitpuller(fname), color, text_color)
        for fname, lbl, desc in items
    )
    return f'<div style="margin:12px 0;">\n{buttons}\n</div>'

def _section_html(heading, items, color, text_color):
    return (
        f'<hr>\n<h2>{heading}</h2>\n'
        + _button_group_html(items, color, text_color)
    )

def _resources_html():
    return """<hr>
<h2>🔗 Resources</h2>
<ul>
  <li><a href="https://inferentialthinking.com/chapters/intro.html" target="_blank">Inferential Thinking — Online Textbook</a></li>
  <li><a href="http://data8.org/datascience/index.html" target="_blank">Datascience Table Reference</a></li>
  <li><a href="https://laserchemist.github.io/dprimer/intro.html" target="_blank">Data Science Primer</a></li>
  <li><a href="https://sites.temple.edu/data/" target="_blank">EDS Course Website</a></li>
</ul>"""

# ── header builders ───────────────────────────────────────────────────────────

def _ms_header_html():
    return (
        '<img src="Temple_flag_morn.png" alt="Temple University" '
        'style="width:180px;float:right;margin:8px;"/>\n'
        '<h1>🔬 STEM Data Science</h1>\n'
        '<h3>Temple University · Summer Program · Middle School</h3>\n'
        '<hr>'
    )

def _hs_header_html():
    return (
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
        '</div>\n<hr>'
    )

def _chem_header_html():
    return (
        '<div style="'
        'background:linear-gradient(135deg,#A10100,#DA1F05,#F33C04,#FE650D,#FFC11F,#FFF75D);'
        'border-radius:14px;padding:28px 32px;margin-bottom:18px;'
        'box-shadow:0 4px 24px rgba(200,0,160,0.35);">\n'
        '  <img src="Temple_flag_morn.png" alt="Temple University" '
        'style="width:140px;float:right;margin:0 0 8px 16px;'
        'border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.4);"/>\n'
        '  <span style="font-size:2.2em;font-weight:900;'
        'background:linear-gradient(90deg,#FFF75D,#FFC11F,#FE650D,#F33C04,#DA1F05,#A10100);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'display:block;line-height:1.2;">⚡ STEM-UP Chemistry</span>\n'
        '  <span style="color:#ffffff;font-size:1.15em;font-weight:600;'
        'text-shadow:0 1px 4px rgba(0,0,0,0.5);">'
        'Temple University · Summer Program · High School</span>\n'
        '</div>\n<hr>'
    )

# ── HTML page writer ──────────────────────────────────────────────────────────

def _write_toc_html(
    output, title, header_html, activities,
    btn_color, include_main, include_reviews, include_exercises,
    include_chemistry, include_instructor, include_final,dark_bg=False,
):
    body_parts = [
        header_html,
        '<p><em>Click any button to open the notebook on the hub.</em></p>',
    ]

    if include_chemistry:
        body_parts.append(
            _section_html("🧪 Chemistry Postlabs and Activities", CHEMISTREES, LIGHTBLUE, "black")
        )

    if include_main:
        body_parts.append("<h2>📚 Activities &amp; Labs</h2>")
        body_parts.append(_button_group_html(activities, btn_color, "white"))

    if include_reviews:
        body_parts.append(_section_html("🧠 Reviews", REVIEWS, GREEN, "white"))
    if include_exercises:
        body_parts.append(_section_html("💪 Exercises", EXERCISES, GOLD, "black"))
    if include_final:
        body_parts.append(_section_html("😱 Final Project", GROUP_PROJ, CRIMSON, "white"))
    if include_instructor:
        body_parts.append(_section_html("🔒 Instructor", INSTRUCTOR, GREY, "white"))

    body_parts.append(_resources_html())

    body_content = "\n\n".join(body_parts)

    if dark_bg:
        body_content = (
            '<div style="background:#1a1a2e;color:#e8e8f0;'
            'padding:24px 28px;border-radius:12px;'
            'box-shadow:0 4px 20px rgba(0,0,0,0.5);">\n'
            + body_content
            + "\n</div>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 960px;
      margin: 0 auto;
      padding: 24px 20px 48px;
      line-height: 1.5;
    }}
    a {{ color: inherit; }}
    hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
    ul {{ padding-left: 1.4em; }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
{body_content}
</body>
</html>"""

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Written → {output}")
    print(f"  Link    → {toc_linker(output)}")

# ── public builders ───────────────────────────────────────────────────────────

def build_ms_toc():
    """Middle school — full (with instructor section). Keep link private."""
    print("\n📘 Middle School — Full TOC")
    _write_toc_html(
        "TOC.html", "STEM Data Science — Middle School",
        _ms_header_html(), MS_ACTIVITIES, CHERRY, include_main=True,
        include_reviews=True, include_exercises=True,
        include_chemistry=False, include_instructor=True, include_final=False
    )

def build_ms_toc_student():
    """Middle school — student-only. Share this link freely."""
    print("\n📘 Middle School — Student TOC")
    _write_toc_html(
        "TOC_student.html", "STEM Data Science — Middle School",
        _ms_header_html(), MS_ACTIVITIES, CHERRY, include_main=True,
        include_reviews=True, include_exercises=True,
        include_chemistry=False, include_instructor=False, include_final=False
    )

def build_hs_toc():
    """High school — full (with instructor section). Keep link private."""
    print("\n🔥 High School — Full TOC")
    _write_toc_html(
        "TOC_hs.html", "STEM Data Science — High School",
        _hs_header_html(), HS_ACTIVITIES, HS_PURPLE, include_main=True,
        include_reviews=True, include_exercises=True,
        include_chemistry=False, include_instructor=True, include_final=True,
        dark_bg=True,
    )

def build_hs_toc_student():
    """High school — student-only. Share this link freely."""
    print("\n🔥 High School — Student TOC")
    _write_toc_html(
        "TOC_hs_student.html", "STEM Data Science — High School",
        _hs_header_html(), HS_ACTIVITIES, HS_PURPLE, include_main=True,
        include_reviews=True, include_exercises=True,
        include_chemistry=False, include_instructor=False, include_final=True,
        dark_bg=True,
    )

def build_toc_chemistry():
    """Chemistry — student-only."""
    print("\n🧪 Chemistry — Student TOC")
    _write_toc_html(
        "TOC_chem.html", "STEM-UP Chemistry",
        _chem_header_html(), HS_ACTIVITIES, HS_PURPLE,
        include_reviews=True, include_exercises=True, include_main=False,
        include_chemistry=True, include_instructor=False, include_final=False
    )

# ── run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_ms_toc()
    build_ms_toc_student()
    build_hs_toc()
    build_hs_toc_student()
    build_toc_chemistry()

    print("\n" + "=" * 60)
    print("SHARE WITH STUDENTS:")
    print("  Middle school → TOC_student.html link above")
    print("  High school   → TOC_hs_student.html link above")
    print("  Chemistry     → TOC_chem.html link above")
    print("\nKEEP PRIVATE (instructor section):")
    print("  Middle school → TOC.html link above")
    print("  High school   → TOC_hs.html link above")
    print("\nOpen in JupyterLab via:")
    print("  File > Open from Path  →  TOC_student.html")
    print("  (JupyterLab renders HTML files inline — no kernel needed)")
