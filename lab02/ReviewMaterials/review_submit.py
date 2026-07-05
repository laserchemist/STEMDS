
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
import json, os, re, glob, time
import numpy as np
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import matplotlib
import matplotlib.pyplot as plt
plt.style.use("ggplot")
# Note: %matplotlib inline must be called in the notebook setup cell
import math
import nbformat as nbf
from datascience import *
from gofer.ok import check
from jupyterquiz import display_quiz
import random as _r

notebook = max(glob.glob('*.ipynb'), key=os.path.getmtime)

BASE_DIR = os.path.dirname(os.path.abspath("review_submit.py"))
path = os.path.join(BASE_DIR, "CodeBuilder2.html")

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

# ── configuration ─────────────────────────────────────────────────────────────

REVIEW_ID = "unknown"   # always pass review_id= explicitly in submit_review()

# Google Sheets — primary submission target
SHEET_ID   = "1JTlIyJCAGE7obspq04ERJkQHOku_d8jZn1sxmIedWJU"

# Credentials in /home/jovyan/shared/ — readable by all hub users (read-only mount)
CREDS_PATH = "/home/jovyan/shared/nordic-knowledge-6598a7fdb7c8.json"

# Per-student fallback — always writable regardless of hub configuration
FALLBACK_JSON = os.path.expanduser("~/submissions_local.json")

# -- ya boi code the builder ---------------------------------------------------

def codebuilder(level, CB_WIDGETS):

    if level not in CB_WIDGETS:

        uid = _r.randint(100000,999999)

        state = widgets.Textarea(
            value="{}",
            layout=widgets.Layout(display="none")
        )

        state.add_class(f"cb-state-{uid}")

        CB_WIDGETS[level] = {
            "uid": uid,
            "state": state
        }

    uid = CB_WIDGETS[level]["uid"]
    state = CB_WIDGETS[level]["state"]

    with open(path, encoding="utf-8") as f:
        html = f.read()

    html = (
        html.replace("%%UID%%", str(uid))
            .replace("__LEVEL__", f"level{level}")
    )

    display(state)
    display(HTML(html))

    return state

def save_cb_state(CB_WIDGETS, path="cb_state.json"):
    data = {}

    for level, obj in CB_WIDGETS.items():
        raw = obj["state"].value
        print("RAW:", level, raw[:50])  # DEBUG

        try:
            parsed = json.loads(raw)
            data[level] = parsed
        except Exception as e:
            print(f"❌ Level {level} failed JSON parse:", e)

    print("FINAL DATA:", data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ wrote file")

def load_cb_state(path="cb_state.json"):
    if not os.path.exists(path):
        print("⚠️ No saved state found")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    CB_WIDGETS = {}

    for level, payload in data.items():
        uid = payload["uid"]

        # IMPORTANT: re-stringify so your JS still works
        state = widgets.Textarea(
            value=json.dumps(payload),
            layout=widgets.Layout(display="none")
        )
        state.add_class(f"cb-state-{uid}")

        CB_WIDGETS[int(level)] = {
            "uid": uid,
            "state": state
        }

    print(f"✅ Loaded {len(CB_WIDGETS)} codebuilders")
    return CB_WIDGETS

def cb_summary(CB_WIDGETS):
    codelist = []
    score = []
    closestTotal = []
    percentage = []
    
    for i in CB_WIDGETS:
        data = json.loads(CB_WIDGETS[i]["state"].value)
        codelist.append(data["response"]["code"])
        score.append(data["evaluation"]["bestMatch"])
        closestTotal.append(data["evaluation"]["bestLength"])
        if data["evaluation"]["bestLength"] > 0:
            percentage.append(data["evaluation"]["bestMatch"]/data["evaluation"]["bestLength"])
        else:
            percentage.append(0)

    
    summary_table = Table().with_columns('number', list(CB_WIDGETS.keys()), 'code', codelist, 'score', score, 'out of', closestTotal, 'percentage', percentage)
    return summary_table

def questions(lab, level):
    with open("Q" + str(lab) + '_' + str(level) + ".json", "r") as file:
        questions=json.load(file)    
    display_quiz(questions)


# ── internal helpers ──────────────────────────────────────────────────────────

def _find_notebook():
    nbs = glob.glob("*.ipynb")
    return max(nbs, key=os.path.getmtime) if nbs else None


def _extract_open_ended(nb_path):
    """
    For every check('secret_code.py') code cell, walk backwards
    up to 6 cells and grab the nearest preceding markdown cell.
    Returns ({q_id: answer_text}, [debug_lines]).
    """
    answers = {}
    debug   = []

    try:
        import nbformat as nbf
        ntbk  = nbf.read(nb_path, nbf.NO_CONVERT)
        cells = ntbk.cells
        debug.append(f"nbformat read OK — {len(cells)} cells")
    except Exception as e:
        debug.append(f"nbformat failed ({e}), falling back to json.load")
        try:
            with open(nb_path, encoding="utf-8") as f:
                raw = json.load(f)
            class _Cell:
                def __init__(self, d):
                    self.cell_type = d.get("cell_type", "")
                    src = d.get("source", [])
                    self.source = src if isinstance(src, str) else "".join(src)
            cells = [_Cell(c) for c in raw.get("cells", [])]
            debug.append(f"json.load fallback OK — {len(cells)} cells")
        except Exception as e2:
            debug.append(f"json.load also failed: {e2}")
            return answers, debug

    for i, cell in enumerate(cells):
        if cell.cell_type != "code":
            continue
        src = cell.source if isinstance(cell.source, str) else "".join(cell.source)
        m = re.search(r'check\s*\(\s*["\'](.+?\.py)["\']\s*\)', src)
        
        if m is None:
            continue
        
        q_id = m.group(1).removesuffix(".py")
        
        debug.append(f"Found check cell for q{q_id} at cell index {i}")
        found = False
        for j in range(i - 1, max(i - 7, -1), -1):
            c = cells[j]
            if c.cell_type == "markdown":
                text = c.source if isinstance(c.source, str) else "".join(c.source)
                answers[q_id] = text.strip()
                debug.append(f"  → captured cell {j}: {text.strip()[:80]!r}")
                found = True
                break
        if not found:
            debug.append(f"  → no markdown cell found within 6 cells above")

    return answers, debug


def _append_to_fallback(path, record):
    """Append record to a local JSON array file in the student's home dir."""
    path = os.path.expanduser(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = [data]
        else:
            data = []
        data.append(record)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True, ""
    except Exception as e:
        return False, str(e)


def _flatten_record(record):
    """Flatten answers dict into spreadsheet columns."""
    flat = {k: v for k, v in record.items() if k != "answers"}
    for i, (q_id, text) in enumerate(record.get("answers", {}).items(), start=1):
        flat[f"open{i}_label"] = q_id
        flat[f"open{i}"]       = text
    return flat


def _append_to_sheet(record, sheet_id, creds_path):
    """
    Append one row to Google Sheets via service account.
    Returns (True, "") on success or (False, error_message) on failure.
    Compatible with gspread v5 and v6.
    """
    try:
        import gspread
    except ImportError:
        return False, "gspread not installed"

    if not os.path.exists(creds_path):
        return False, (
            f"Credentials not found at {creds_path}\n"
            f"     Ensure the file is at /home/jovyan/shared/ "
            f"(readable by all hub users)."
        )

    try:
        try:
            gc = gspread.service_account(filename=creds_path)
        except AttributeError:
            from google.oauth2.service_account import Credentials
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds  = Credentials.from_service_account_file(creds_path, scopes=scopes)
            gc     = gspread.authorize(creds)

        ws   = gc.open_by_key(sheet_id).sheet1
        flat = _flatten_record(record)
        existing_headers = ws.row_values(1)

        if not existing_headers:
            ws.append_row(list(flat.keys()), value_input_option="RAW")
            ws.append_row(list(flat.values()), value_input_option="USER_ENTERED")
        else:
            new_cols = [k for k in flat if k not in existing_headers]
            if new_cols:
                updated_headers = existing_headers + new_cols
                ws.update(range_name="A1", values=[updated_headers])
            else:
                updated_headers = existing_headers
            row = [flat.get(col, "") for col in updated_headers]
            ws.append_row(row, value_input_option="USER_ENTERED")

        return True, ""

    except Exception as e:
        return False, str(e)


# ── public API ────────────────────────────────────────────────────────────────

def submit_review(name, user, CB_WIDGETS, review_id=REVIEW_ID):
    percentage = []
    
    for i in CB_WIDGETS:
        data = json.loads(CB_WIDGETS[i]["state"].value)
        eval_data = data.get("evaluation", {})
        best = eval_data.get("bestMatch", 0)
        length = eval_data.get("bestLength", 0)
        if length > 0:
            percentage.append(best/length)
        else:
            percentage.append(0)

    totalscore = sum(percentage)*3

    print(f"Score: {totalscore:.1f}/18")
    print(f"Note: this doesn't take into account the secret code. >:P")

    btn = widgets.Button(
        description  = "Submit Review",
        button_style = "success",
        icon         = "check",
        layout       = widgets.Layout(width="180px", height="40px"),
        style        = {"font_weight": "bold"},
    )
    out = widgets.Output()

    def _on_click(b):
        b.disabled = True
        with out:
            clear_output(wait=True)
            try:
                from IPython.display import Javascript
                display(Javascript("""
                    (function() {
                        try { IPython.notebook.save_checkpoint(); } catch(e) {}
                        try { window.jupyterapp.commands.execute('docmanager:save'); } catch(e) {}
                    })();
                """))
                print("💾  Saving notebook…")
                time.sleep(2)
                clear_output(wait=True)

                nb_path   = _find_notebook()
                localtime = time.asctime(time.localtime(time.time()))

                if nb_path:
                    answers, _debug = _extract_open_ended(nb_path)
                else:
                    answers = {}

                record = {
                    "lab":       review_id,
                    "name":      name,
                    "user":      user,
                    "timestamp": localtime,
                    "score_pct": round(totalscore/18, 1),
                    "correct":   totalscore,
                    "total":     18,
                    "notebook":  nb_path or "unknown",
                    "answers":   answers,
                }

                destinations = []
                warnings     = []

                # ── Target 1: Google Sheets ───────────────────────────────
                if SHEET_ID:
                    ok, err = _append_to_sheet(record, SHEET_ID, CREDS_PATH)
                    if ok:
                        destinations.append("Google Sheets")
                    else:
                        warnings.append(f"Google Sheets: {err}")

                # ── Target 2: Student home fallback ───────────────────────
                ok, err = _append_to_fallback(FALLBACK_JSON, record)
                if ok:
                    destinations.append(FALLBACK_JSON)
                else:
                    warnings.append(f"Local fallback: {err}")

                b.description  = "Submitted ✓"
                b.button_style = "info"

                print(f"✅  Submitted {review_id} for {name}")
                print(f"    Time    : {localtime}")
                print(f"    Score   : {totalscore:.1f}/18")
                print(f"    Answers : {len(answers)} open-ended response(s) captured")
                print(f"    Saved   : {', '.join(destinations) or 'nowhere — see warnings'}")

                for w in warnings:
                    print(f"  ⚠️  {w}")

                if not destinations:
                    print("  ❌  No submission was saved. Contact your instructor.")

                if not answers:
                    print("\n  ⚠️  No open-ended answers captured.")
                    print("     Make sure you typed in the markdown cells above each check().")

            except Exception as e:
                b.disabled     = False
                b.button_style = "danger"
                print(f"❌  Submission failed: {e}")

    btn.on_click(_on_click)
    display(widgets.VBox([btn, out]))


def submit_quiz(name, user, quiz_score, quiz_total, quiz_id="Quiz"):
    """
    Submit function for quiz notebooks (no gofer checks).

        from lab_submit import submit_quiz
        submit_quiz(name, user, score, total, quiz_id="Quiz03")
    """
    if quiz_total == 0:
        print("❌  quiz_total is 0 — cannot compute score.")
        return

    perc_correct = quiz_score / quiz_total * 100
    msg = "great score!" if perc_correct >= 80 else \
          "review the material and try again!"

    print(f"----\n{name} — {msg}\n----\nusername: {user}")
    print(f"Quiz score: {perc_correct:.1f}%  ({quiz_score}/{quiz_total})")

    btn = widgets.Button(
        description  = "Submit Quiz",
        button_style = "warning",
        icon         = "check",
        layout       = widgets.Layout(width="180px", height="40px"),
        style        = {"font_weight": "bold"},
    )
    out = widgets.Output()

    def _on_click(b):
        b.disabled = True
        with out:
            clear_output(wait=True)
            try:
                from IPython.display import Javascript
                display(Javascript("""
                    (function() {
                        try { IPython.notebook.save_checkpoint(); } catch(e) {}
                        try { window.jupyterapp.commands.execute('docmanager:save'); } catch(e) {}
                    })();
                """))
                print("💾  Saving…")
                time.sleep(2)
                clear_output(wait=True)

                nb_path   = _find_notebook()
                localtime = time.asctime(time.localtime(time.time()))

                record = {
                    "lab":       quiz_id,
                    "name":      name,
                    "user":      user,
                    "timestamp": localtime,
                    "score_pct": round(perc_correct, 1),
                    "correct":   quiz_score,
                    "total":     quiz_total,
                    "notebook":  nb_path or "unknown",
                    "answers":   {},
                }

                destinations = []
                warnings     = []

                if SHEET_ID:
                    ok, err = _append_to_sheet(record, SHEET_ID, CREDS_PATH)
                    if ok:
                        destinations.append("Google Sheets")
                    else:
                        warnings.append(f"Google Sheets: {err}")

                ok, err = _append_to_fallback(FALLBACK_JSON, record)
                if ok:
                    destinations.append(FALLBACK_JSON)
                else:
                    warnings.append(f"Local fallback: {err}")

                b.description  = "Submitted ✓"
                b.button_style = "info"

                print(f"✅  Submitted {quiz_id} for {name}")
                print(f"    Time  : {localtime}")
                print(f"    Score : {perc_correct:.1f}%  ({quiz_score}/{quiz_total})")
                print(f"    Saved : {', '.join(destinations) or 'nowhere — see warnings'}")

                for w in warnings:
                    print(f"  ⚠️  {w}")

            except Exception as e:
                b.disabled     = False
                b.button_style = "danger"
                print(f"❌  Submission failed: {e}")

    btn.on_click(_on_click)
    display(widgets.VBox([btn, out]))
