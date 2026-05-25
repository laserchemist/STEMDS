"""
Instructor Submission Dashboard
================================
Works with both /home/jovyan/shared/submissions.json and Google Sheets.
Run as a notebook cell or standalone script from your instructor account.
"""

import json, os, pandas as pd
from IPython.display import display, clear_output
import ipywidgets as widgets

SHARED_JSON = "/home/jovyan/shared/submissions.json"
SHEET_ID    = None    # set to your sheet ID to also pull from Sheets
CREDS_PATH  = "/home/jovyan/shared/gs_credentials.json"


def load_from_json(path=SHARED_JSON):
    if not os.path.exists(path):
        return pd.DataFrame()
    with open(path) as f:
        records = json.load(f)
    return pd.json_normalize(records)


def load_from_sheets(sheet_id, creds_path):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds  = Credentials.from_service_account_file(creds_path, scopes=scopes)
        gc     = gspread.authorize(creds)
        ws     = gc.open_by_key(sheet_id).sheet1
        rows   = ws.get_all_records()
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"[Sheets] Could not load: {e}")
        return pd.DataFrame()


# Load and merge sources
frames = [load_from_json()]
if SHEET_ID:
    frames.append(load_from_sheets(SHEET_ID, CREDS_PATH))
df = pd.concat(frames, ignore_index=True).drop_duplicates()

if df.empty:
    print("No submissions yet.")
else:
    print(f"{len(df)} total submission(s) loaded.\n")

# ── interactive viewer ────────────────────────────────────────────────────────

labs = sorted(df["lab"].unique()) if "lab" in df.columns else []

lab_dd = widgets.Dropdown(
    options=["All"] + labs,
    description="Lab:",
    layout=widgets.Layout(width="200px"),
)
out = widgets.Output()


def show(change=None):
    with out:
        clear_output(wait=True)
        filt = df if lab_dd.value == "All" else df[df["lab"] == lab_dd.value]

        summary_cols = [c for c in ["lab","name","user","timestamp","score_pct","correct","total"]
                        if c in filt.columns]
        print(f"=== {lab_dd.value} — {len(filt)} submission(s) ===\n")
        display(filt[summary_cols].sort_values("timestamp", ascending=False)
                                  .reset_index(drop=True))

        if "score_pct" in filt.columns:
            bins   = [0, 60, 70, 80, 90, 101]
            labels = ["<60", "60-70", "70-80", "80-90", "90-100"]
            filt = filt.copy()
            filt["_bin"] = pd.cut(filt["score_pct"], bins=bins, labels=labels, right=False)
            print("\nScore distribution:")
            print(filt["_bin"].value_counts().sort_index().to_string())

        # Open-ended answers — latest submission per user
        answer_cols = [c for c in filt.columns
                       if c.startswith("answers.") or c.startswith("answer_")]
        if answer_cols:
            print(f"\n{'─'*60}")
            print("Open-ended answers (most recent per student):")
            latest = (filt.sort_values("timestamp")
                          .drop_duplicates("user", keep="last"))
            for _, row in latest.iterrows():
                print(f"\n── {row.get('name','')} ({row.get('user','')}) ──")
                for col in answer_cols:
                    val = str(row.get(col, "")).strip()
                    if val and val.lower() not in ("nan", "answer", ""):
                        q = col.replace("answers.", "").replace("answer_", "")
                        print(f"  [{q}]\n    {val[:400]}")


lab_dd.observe(show, names="value")
display(widgets.VBox([lab_dd, out]))
show()


# ── export helpers ────────────────────────────────────────────────────────────

def export_csv(lab="all", path=None):
    """Export submissions to CSV. Usage: export_csv("Lab04")"""
    filt = df if lab == "all" else df[df["lab"] == lab]
    out_path = path or f"submissions_{lab}.csv"
    filt.to_csv(out_path, index=False)
    print(f"Exported {len(filt)} rows -> {out_path}")

# export_csv("Lab04")
