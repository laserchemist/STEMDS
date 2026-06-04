"""
lab_submit.py
=============
Drop this file into each lab directory alongside the .ipynb notebook.

Student notebook — final cell (all students see):
─────────────────────────────────────────────────
    from lab_submit import submit_lab
    submit_lab(name, user, correct, questions)
─────────────────────────────────────────────────

Configure LAB_ID below for each lab copy. OPEN_ENDED_IDS is no longer
needed — all open-ended questions are detected automatically.

Write targets (tried in order):
  1. Google Sheets  — via service account (silent if not configured)
  2. Shared folder  — /home/jovyan/shared/submissions.json
  3. Home fallback  — ~/submissions_local.json
"""

import json, os, re, glob, time, fcntl
import ipywidgets as widgets
from IPython.display import display, clear_output

# ── per-lab configuration ─────────────────────────────────────────────────────

LAB_ID = "Lab04"      # ← change this for each lab copy

# ── write targets ─────────────────────────────────────────────────────────────


FALLBACK_JSON = os.path.expanduser("~/submissions_local.json")

# Google Sheets — set SHEET_ID to enable, leave None to skip silently.
SHEET_ID   = "1JTlIyJCAGE7obspq04ERJkQHOku_d8jZn1sxmIedWJU"    # e.g. "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
SHARED_JSON = "/home/jovyan/shared-readwrite/submissions.json"
CREDS_PATH  = "/home/jovyan/shared-readwrite/nordic-knowledge-6598a7fdb7c8.json"

# ── internal helpers ──────────────────────────────────────────────────────────

def _find_notebook():
    nbs = glob.glob("*.ipynb")
    return max(nbs, key=os.path.getmtime) if nbs else None


def _extract_open_ended(nb_path):
    """
    Read the notebook with nbformat (same library EDS_mod.test_open uses)
    so the read behaviour is identical to what the gofer tests already do.

    For every  check('tests/qXX_open_ended.py')  code cell, walk backwards
    up to 6 cells and grab the nearest preceding markdown cell — that is
    what the student typed in place of ANSWER.

    Bug that was here before: the regex captured 'q11_open_ended' (with the
    leading q) but OPEN_ENDED_IDS stored '11_open_ended' (without it), so
    every answer was silently filtered out.  Fixed by moving the q outside
    the capture group and dropping the explicit ID filter entirely — any cell
    matching check('tests/qXX_open_ended.py') is by definition open-ended.

    Returns ({q_id: answer_text}, [debug_lines]).
    """
    answers = {}
    debug   = []

    # ── read with nbformat, exactly like EDS_mod.test_open ───────────────
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
            # Wrap dicts so the rest of the code can use .cell_type / .source
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

        # nbformat stores source as a plain string; json.load gives a list
        src = cell.source if isinstance(cell.source, str) else "".join(cell.source)

        # Capture group starts AFTER the 'q' so we get "11_open_ended" not
        # "q11_open_ended" — matching the convention used in OPEN_ENDED_IDS.
        m = re.search(r'check\s*\(\s*["\']tests/q([^"\']+_open_ended)\.py["\']', src)
        if not m:
            continue

        q_id = m.group(1)   # e.g. "11_open_ended", "9a_open_ended"
        debug.append(f"Found check cell for q{q_id} at cell index {i}")

        # Walk back for the nearest markdown cell
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


def _atomic_append_json(path, record):
    """Append record to a JSON array file with fcntl locking + atomic rename."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    lock_path = path + ".lock"
    with open(lock_path, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
            else:
                data = []
            data.append(record)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, path)
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def _flatten_record(record):
    """
    Flatten for a spreadsheet row.
    answers {q_id: text} → open1_label / open1 / open2_label / open2 / …
    Sequential numbering keeps columns consistent across labs even when
    question IDs differ between Lab04 and Lab05.
    """
    flat = {k: v for k, v in record.items() if k != "answers"}
    for i, (q_id, text) in enumerate(record.get("answers", {}).items(), start=1):
        flat[f"open{i}_label"] = q_id
        flat[f"open{i}"]       = text
    return flat


def _append_to_sheet(record, sheet_id, creds_path):
    """
    Append one row to a Google Sheet via service account.
    Returns (True, "") on success or (False, error_message) on failure
    so the caller can surface the reason rather than silently dropping data.

    Compatible with gspread v5 and v6 (argument order for ws.update changed
    in v6; we use the keyword form which works in both versions).
    Uses gspread.service_account() — the modern API — with a fallback to
    the deprecated gspread.authorize() for older installs.
    """
    try:
        import gspread
    except ImportError:
        return False, "gspread not installed — run: pip install gspread google-auth"

    if not os.path.exists(creds_path):
        return False, f"Credentials file not found: {creds_path}"

    try:
        # Modern API (gspread >= 5.x): service_account() handles auth internally
        try:
            gc = gspread.service_account(filename=creds_path)
        except AttributeError:
            # Very old gspread — fall back to manual Credentials object
            from google.oauth2.service_account import Credentials
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds  = Credentials.from_service_account_file(creds_path, scopes=scopes)
            gc     = gspread.authorize(creds)

        ws   = gc.open_by_key(sheet_id).sheet1
        flat = _flatten_record(record)

        existing_headers = ws.row_values(1)   # [] on an empty sheet

        if not existing_headers:
            # Fresh sheet — write header then data
            ws.append_row(list(flat.keys()), value_input_option="RAW")
            ws.append_row(list(flat.values()), value_input_option="USER_ENTERED")
        else:
            # Extend header rightward if this record has new columns
            # (e.g. first time open-ended answers appear)
            new_cols = [k for k in flat if k not in existing_headers]
            if new_cols:
                updated_headers = existing_headers + new_cols
                # Use keyword args — argument order changed between gspread v5 and v6
                ws.update(range_name="A1", values=[updated_headers])
            else:
                updated_headers = existing_headers

            row = [flat.get(col, "") for col in updated_headers]
            ws.append_row(row, value_input_option="USER_ENTERED")

        return True, ""

    except Exception as e:
        return False, str(e)


# ── public API ────────────────────────────────────────────────────────────────

def submit_lab(name, user, correct, questions, lab_id=LAB_ID):
    """
    Display a score summary and a Submit button.
    Call this as the last cell in any lab notebook:

        from lab_submit import submit_lab
        submit_lab(name, user, correct, questions)
    """
    perc_correct = correct / len(questions) * 100
    msg = "nice work!" if perc_correct >= 80 else "look over your work again, seek help, some errors!!!"

    print(f"----\n{name} {msg}\n----\nusername: {user}")
    print(f"Score: {perc_correct:.1f}%  ({correct}/{len(questions)})")

    btn = widgets.Button(
        description="Submit Lab",
        button_style="success",
        icon="check",
        layout=widgets.Layout(width="180px", height="40px"),
        style={"font_weight": "bold"},
    )
    out = widgets.Output()

    def _on_click(b):
        b.disabled = True
        with out:
            clear_output(wait=True)
            try:
                # Force save — try both JupyterLab and classic Notebook APIs;
                # whichever is inactive silently fails its try/catch in JS.
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
                    answers, debug = _extract_open_ended(nb_path)
                else:
                    answers, debug = {}, ["No .ipynb found in current directory"]

                # Uncomment to debug answer extraction:
                # for line in debug: print("  [debug]", line)

                record = {
                    "lab":       lab_id,
                    "name":      name,
                    "user":      user,
                    "timestamp": localtime,
                    "score_pct": round(perc_correct, 1),
                    "correct":   correct,
                    "total":     len(questions),
                    "notebook":  nb_path or "unknown",
                    "answers":   answers,
                }

                destinations = []

                if SHEET_ID:
                    ok, sheet_err = _append_to_sheet(record, SHEET_ID, CREDS_PATH)
                    if ok:
                        destinations.append("Google Sheets")
                    else:
                        print(f"  \u26a0\ufe0f  Google Sheets write failed: {sheet_err}")

                try:
                    _atomic_append_json(SHARED_JSON, record)
                    destinations.append(SHARED_JSON)
                except (PermissionError, OSError):
                    _atomic_append_json(FALLBACK_JSON, record)
                    destinations.append(FALLBACK_JSON)

                b.description  = "Submitted ✓"
                b.button_style = "info"

                print(f"✅  Submitted {lab_id} for {name}")
                print(f"    Time     : {localtime}")
                print(f"    Score    : {perc_correct:.1f}%  ({correct}/{len(questions)})")
                print(f"    Answers  : {len(answers)} open-ended response(s) captured")
                print(f"    Saved    : {', '.join(destinations)}")

                if not answers:
                    print("\n  ⚠️  No open-ended answers captured.")
                    print("     Uncomment the debug lines in lab_submit.py")
                    print("     to diagnose, then resubmit.")

            except Exception as e:
                b.disabled     = False
                b.button_style = "danger"
                print(f"❌  Submission failed: {e}")

    btn.on_click(_on_click)
    display(widgets.VBox([btn, out]))
