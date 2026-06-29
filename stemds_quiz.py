"""
stemds_quiz.py
==============
Self-contained quiz widget for STEMDS JupyterHub notebooks.
All lockout logic lives here — quiz notebooks stay clean (2 lines of student code).

Lockout persistence uses Google Sheets (a dedicated tab) so it works for
ALL hub users — no shared filesystem required.
Per-question state falls back to the student's home directory.

Student notebook usage (all that students ever see or need)
────────────────────────────────────────────────────────────
    from stemds_quiz import open_quiz
    open_quiz("questions_quiz03.json", name, user)

Instructor configuration (edit this file only)
───────────────────────────────────────────────
    QUIZ_ID          — unique string per quiz, e.g. "Quiz03"
    MAX_ATTEMPTS     — 1 (strict) or 2 (one retry per question)
    INSTRUCTOR_USERS — hub usernames that bypass lockout
    SHEET_ID         — same Google Sheet used by lab_submit.py
    CREDS_PATH       — credentials in /home/jovyan/shared/ (readable by all)

Instructor reset
─────────────────────────────────────────────────────────────
    from stemds_quiz import reset_attempt
    reset_attempt("jsmith@temple.edu", "Quiz03")   # reset one student
    reset_attempt("*", "Quiz03")                   # reset ALL for this quiz
"""

import json, os, time, glob
import ipywidgets as widgets
from IPython.display import display, HTML

# ══════════════════════════════════════════════════════════════════════════════
#  INSTRUCTOR CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

QUIZ_ID      = "Quiz03"
MAX_ATTEMPTS = 1

INSTRUCTOR_USERS = {"laserchemist", "jmsmith1@temple.edu", "instructor", "admin"}

# Google Sheets — same sheet as lab_submit.py, second tab named "quiz_attempts"
SHEET_ID   = "1JTlIyJCAGE7obspq04ERJkQHOku_d8jZn1sxmIedWJU"
CREDS_PATH = "/home/jovyan/shared/nordic-knowledge-6598a7fdb7c8.json"

# Per-student state file fallback (home dir — always writable)
_STATE_DIR = os.path.expanduser("~/.stemds_quiz")

# ── colours ────────────────────────────────────────────────────────────────────
_C = dict(
    cherry     = "#9B2335",
    navy       = "#1a3a5c",
    green      = "#1a6e2e",
    red        = "#c0392b",
    amber      = "#e67e22",
    blue       = "#2980b9",
    bg_q       = "#eaf4fb",
    bg_lock    = "#fdf3f3",
    bg_done    = "#f0fff0",
    pale_green = "#c8f7c5",
    white      = "#ffffff",
    light_grey = "#f5f5f5",
)

# ══════════════════════════════════════════════════════════════════════════════
#  GOOGLE SHEETS LOCKOUT PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════

def _get_sheet_tab(tab_name="quiz_attempts"):
    """
    Open (or create) a worksheet tab in the shared Google Sheet.
    Returns the worksheet object or None on failure.
    """
    try:
        import gspread
    except ImportError:
        return None, "gspread not installed"

    if not os.path.exists(CREDS_PATH):
        return None, f"Credentials not found: {CREDS_PATH}"

    try:
        try:
            gc = gspread.service_account(filename=CREDS_PATH)
        except AttributeError:
            from google.oauth2.service_account import Credentials
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds  = Credentials.from_service_account_file(CREDS_PATH, scopes=scopes)
            gc     = gspread.authorize(creds)

        spreadsheet = gc.open_by_key(SHEET_ID)

        # Get or create the quiz_attempts tab
        try:
            ws = spreadsheet.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=6)
            ws.append_row(["user", "quiz_id", "name", "timestamp", "status"],
                          value_input_option="RAW")
        return ws, ""

    except Exception as e:
        return None, str(e)


def _sheet_read_attempt(user, quiz_id):
    """
    Look up existing attempt record in the Sheet.
    Returns record dict or None if not found.
    """
    ws, err = _get_sheet_tab()
    if ws is None:
        return None   # can't read — treat as no attempt (fail open)

    try:
        records = ws.get_all_records()
        for r in records:
            if r.get("user") == user and r.get("quiz_id") == quiz_id:
                return r
    except Exception:
        pass
    return None


def _sheet_write_attempt(user, quiz_id, name):
    """
    Write a new attempt record to the Sheet.
    Returns (True, "") or (False, error).
    """
    ws, err = _get_sheet_tab()
    if ws is None:
        return False, err

    try:
        ws.append_row(
            [user, quiz_id, name, time.asctime(), "opened"],
            value_input_option="USER_ENTERED"
        )
        return True, ""
    except Exception as e:
        return False, str(e)


def _sheet_delete_attempt(user, quiz_id):
    """
    Delete attempt rows for user+quiz_id. Used by reset_attempt().
    Returns count of rows deleted.
    """
    ws, err = _get_sheet_tab()
    if ws is None:
        return 0

    try:
        all_values = ws.get_all_values()
        if not all_values:
            return 0

        header = all_values[0]
        user_col = header.index("user") if "user" in header else 0
        quiz_col = header.index("quiz_id") if "quiz_id" in header else 1

        # Find rows to delete (work backwards so indices stay valid)
        to_delete = [
            i + 1   # 1-indexed for gspread
            for i, row in enumerate(all_values[1:], start=1)
            if (user == "*" or row[user_col] == user)
            and row[quiz_col] == quiz_id
        ]

        for row_idx in reversed(to_delete):
            ws.delete_rows(row_idx)

        return len(to_delete)
    except Exception:
        return 0


# ══════════════════════════════════════════════════════════════════════════════
#  PER-QUESTION STATE (home directory — always writable)
# ══════════════════════════════════════════════════════════════════════════════

def _state_path(user, quiz_id):
    safe_user = user.replace("@", "_").replace(".", "_")
    return os.path.join(_STATE_DIR, f"{safe_user}_{quiz_id}_state.json")

def _load_state(user, quiz_id):
    path = _state_path(user, quiz_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None

def _save_state(user, quiz_id, state):
    os.makedirs(_STATE_DIR, exist_ok=True)
    path = _state_path(user, quiz_id)
    tmp  = path + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass   # silent — state is best-effort

def _delete_state(user, quiz_id):
    path = _state_path(user, quiz_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC INSTRUCTOR TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def reset_attempt(user, quiz_id=None):
    """
    Reset quiz attempt for one student or all students.

        reset_attempt("jsmith@temple.edu", "Quiz03")
        reset_attempt("*", "Quiz03")   # reset everyone
    """
    quiz_id = quiz_id or QUIZ_ID

    # Delete Sheet lockout record
    n_sheet = _sheet_delete_attempt(user, quiz_id)

    # Delete local state file(s)
    if user == "*":
        n_state = 0
        if os.path.isdir(_STATE_DIR):
            for f in glob.glob(os.path.join(_STATE_DIR, f"*_{quiz_id}_state.json")):
                os.remove(f)
                n_state += 1
    else:
        n_state = 1 if _delete_state(user, quiz_id) else 0

    if n_sheet or n_state:
        print(f"✅ Reset {quiz_id} for user='{user}'")
        print(f"   Sheet rows removed : {n_sheet}")
        print(f"   State files removed: {n_state}")
    else:
        print(f"ℹ️  No attempt found for user='{user}' quiz='{quiz_id}'")


def list_attempts(quiz_id=None):
    """
    Print all attempt records for a quiz from the Sheet.

        list_attempts("Quiz03")
    """
    quiz_id = quiz_id or QUIZ_ID
    ws, err = _get_sheet_tab()
    if ws is None:
        print(f"❌ Cannot read Sheet: {err}")
        return

    try:
        records = [r for r in ws.get_all_records()
                   if r.get("quiz_id") == quiz_id]
        if not records:
            print(f"No attempts recorded for {quiz_id}")
            return
        print(f"\n{quiz_id} — {len(records)} attempt(s):\n")
        for r in records:
            print(f"  {r.get('user','?'):35s} {r.get('name','?'):20s} {r.get('timestamp','?')}")
    except Exception as e:
        print(f"❌ Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  QUESTION WIDGET (unchanged from previous version)
# ══════════════════════════════════════════════════════════════════════════════

class _QuestionWidget:

    def __init__(self, idx, q_data, max_attempts, on_change, init_state=None):
        self.idx          = idx
        self.data         = q_data
        self.max_attempts = max_attempts
        self._on_change   = on_change

        self.attempts_used      = 0
        self.locked             = False
        self.answered_correctly = False

        if init_state:
            self.attempts_used      = init_state.get("attempts_used", 0)
            self.locked             = init_state.get("locked", False)
            self.answered_correctly = init_state.get("answered_correctly", False)

        self._build()

    def _build(self):
        answers   = self.data["answers"]
        remaining = self.max_attempts - self.attempts_used

        if self.locked and self.answered_correctly:
            hdr_bg, hdr_icon = _C["green"], "✅"
        elif self.locked:
            hdr_bg, hdr_icon = _C["red"],   "🔒"
        else:
            hdr_bg, hdr_icon = _C["cherry"], f"Q{self.idx + 1}"

        header = widgets.HTML(
            f'<div style="background:{hdr_bg};color:{_C["white"]};'
            f'border-radius:6px 6px 0 0;padding:8px 14px;font-weight:700;">'
            f'{hdr_icon} &nbsp; {self.data["question"]}</div>'
        )

        self._attempt_label = widgets.HTML(self._attempt_html(remaining))
        self._feedback      = widgets.Output()
        self._answer_btns   = []
        btn_children        = []

        for i, ans in enumerate(answers):
            if self.locked and ans["correct"]:
                bg, fg, cursor = _C["pale_green"], "#1a3a2e", "default"
            elif self.locked:
                bg, fg, cursor = _C["light_grey"], "#888", "default"
            else:
                bg, fg, cursor = _C["light_grey"], "#222", "pointer"

            html_w = widgets.HTML(
                f'<div style="background:{bg};color:{fg};'
                f'border-radius:6px;padding:9px 16px;'
                f'font-size:0.97em;font-weight:500;cursor:{cursor};'
                f'border:1px solid #ddd;line-height:1.4;">'
                f'{ans["answer"]}</div>'
            )
            html_w._ans_index = i

            click_btn = widgets.Button(
                description = "▶",
                tooltip     = "Select this answer",
                layout      = widgets.Layout(width="44px", height="40px",
                                             margin="0px 4px 0px 0px"),
                style       = {"button_color": bg, "font_weight": "700"},
            )
            click_btn._ans_index = i
            click_btn._html_w    = html_w

            if not self.locked:
                click_btn.on_click(self._on_click)
            else:
                click_btn.disabled = True

            row = widgets.HBox(
                [click_btn, html_w],
                layout=widgets.Layout(width="96%", margin="2px 0",
                                      align_items="center")
            )
            self._answer_btns.append((html_w, click_btn))
            btn_children.append(row)

        btn_area = widgets.VBox(btn_children,
                                layout=widgets.Layout(padding="4px 10px"))

        border = (_C["green"] if (self.locked and self.answered_correctly)
                  else _C["red"] if self.locked else _C["blue"])

        self.widget = widgets.VBox(
            [header, self._attempt_label, btn_area, self._feedback],
            layout=widgets.Layout(border=f"1px solid {border}",
                                  border_radius="8px", margin="10px 0")
        )

    def _attempt_html(self, remaining):
        if self.locked and self.answered_correctly:
            txt = f'<span style="color:{_C["green"]};font-size:0.88em;">✅ Correct!</span>'
        elif self.locked:
            txt = f'<span style="color:{_C["red"]};font-size:0.88em;">🔒 No attempts remaining</span>'
        else:
            txt = (f'<span style="color:{_C["blue"]};font-size:0.88em;">'
                   f'Attempts remaining: <b>{remaining}</b> of {self.max_attempts}</span>')
        return f'<div style="padding:4px 14px 2px 14px;">{txt}</div>'

    def _on_click(self, btn):
        if self.locked:
            return

        i          = btn._ans_index
        html_w     = btn._html_w
        ans        = self.data["answers"][i]
        is_correct = ans["correct"]
        feedback   = ans.get("feedback", "")

        self.attempts_used += 1
        remaining = self.max_attempts - self.attempts_used

        row_bg = _C["green"] if is_correct else _C["red"]
        row_fg = _C["white"]
        html_w.value = (
            f'<div style="background:{row_bg};color:{row_fg};'
            f'border-radius:6px;padding:9px 16px;'
            f'font-size:0.97em;font-weight:600;cursor:default;'
            f'border:1px solid {row_bg};line-height:1.4;">'
            f'{ans["answer"]}</div>'
        )
        btn.style.button_color = row_bg
        btn.style.text_color   = row_fg
        if not is_correct:
            btn.disabled = True

        if is_correct:
            self.answered_correctly = True
            self.locked = True
            fb = (f'<div style="background:{_C["bg_done"]};border-left:5px solid {_C["green"]};'
                  f'padding:10px 14px;border-radius:6px;margin:6px 0;">'
                  f'✅ <b>Correct!</b>'
                  + (f' &nbsp;— {feedback}' if feedback else '') + '</div>')
        elif remaining > 0:
            fb = (f'<div style="background:#fff8f8;border-left:5px solid {_C["red"]};'
                  f'padding:10px 14px;border-radius:6px;margin:6px 0;">'
                  f'❌ <b>Not quite.</b>'
                  + (f' &nbsp;— {feedback}' if feedback else '')
                  + f' <i>({remaining} attempt{"s" if remaining!=1 else ""} left)</i></div>')
        else:
            self.locked = True
            correct_ans = next(a for a in self.data["answers"] if a["correct"])
            fb = (f'<div style="background:{_C["bg_lock"]};border-left:5px solid {_C["red"]};'
                  f'padding:10px 14px;border-radius:6px;margin:6px 0;">'
                  f'❌ <b>No attempts remaining.</b>'
                  + (f' &nbsp;— {feedback}' if feedback else '')
                  + f'<br><br>✅ <b>Correct answer:</b> {correct_ans["answer"]}'
                  + (f'<br><i>{correct_ans.get("feedback","")}</i>'
                     if correct_ans.get("feedback") else '')
                  + '</div>')

        with self._feedback:
            self._feedback.clear_output(wait=True)
            display(HTML(fb))

        if self.locked:
            for html_w2, btn2 in self._answer_btns:
                btn2.disabled = True
                ans2 = self.data["answers"][btn2._ans_index]
                if ans2["correct"] and not (is_correct and btn2._ans_index == i):
                    html_w2.value = (
                        f'<div style="background:{_C["pale_green"]};color:#1a3a2e;'
                        f'border-radius:6px;padding:9px 16px;'
                        f'font-size:0.97em;font-weight:600;cursor:default;'
                        f'border:1px solid {_C["green"]};line-height:1.4;">'
                        f'{ans2["answer"]}</div>'
                    )
                    btn2.style.button_color = _C["pale_green"]

        self._attempt_label.value = self._attempt_html(remaining)
        self._on_change()

    def get_state(self):
        return {
            "attempts_used":      self.attempts_used,
            "locked":             self.locked,
            "answered_correctly": self.answered_correctly,
        }


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def open_quiz(questions_source, name, user,
              quiz_id=None, max_attempts=None, n_questions=None):
    """
    The only function students ever call.

    Parameters
    ──────────
    questions_source : str — path to JSON file
    name             : str — student name
    user             : str — JupyterHub username (from lab_init: user)
    quiz_id          : str — overrides module-level QUIZ_ID
    max_attempts     : int — overrides module-level MAX_ATTEMPTS
    n_questions      : int — randomly select this many from the full bank
                             (seeded by username+quiz_id for consistency)
    """
    qid = quiz_id      or QUIZ_ID
    mxa = max_attempts or MAX_ATTEMPTS

    is_instructor = (user in INSTRUCTOR_USERS)

    # ── instructor banner ──────────────────────────────────────────────────
    if is_instructor:
        display(HTML(
            f'<div style="background:{_C["amber"]};color:{_C["white"]};'
            f'border-radius:8px;padding:10px 16px;margin:8px 0;font-weight:700;">'
            f'🧪 Instructor mode — lockout bypassed for <code>{user}</code>'
            f'</div>'
        ))

    # ── lockout check via Google Sheets ───────────────────────────────────
    if not is_instructor:
        rec = _sheet_read_attempt(user, qid)
        if rec:
            display(HTML(
                f'<div style="background:{_C["bg_lock"]};'
                f'border-left:6px solid {_C["red"]};'
                f'border-radius:8px;padding:16px 20px;margin:12px 0;">'
                f'<b style="font-size:1.1em;">🔒 Quiz already opened</b><br><br>'
                f'This quiz was opened by <b>{rec.get("name", user)}</b> '
                f'on {rec.get("timestamp", "unknown time")}.<br>'
                f'Only one attempt is allowed. '
                f'Contact your instructor if this is an error.'
                f'</div>'
            ))

            class _Locked:
                score  = 0
                total  = 0
                locked = True
                def __iter__(self): yield 0; yield 0
            return _Locked()

        # Record the opening in the Sheet
        ok, err = _sheet_write_attempt(user, qid, name)
        if not ok:
            # Sheet write failed — warn but continue (fail open for students)
            display(HTML(
                f'<div style="background:#fff3cd;border-left:5px solid {_C["amber"]};'
                f'padding:10px 14px;border-radius:6px;margin:6px 0;">'
                f'⚠️ Could not record attempt ({err}). '
                f'Please notify your instructor before closing this notebook.'
                f'</div>'
            ))

    # ── load questions ─────────────────────────────────────────────────────
    if isinstance(questions_source, str):
        with open(questions_source, encoding="utf-8") as f:
            all_questions = json.load(f)
    else:
        all_questions = list(questions_source)

    # ── random subset (seeded per user — same questions on reconnect) ──────
    if n_questions and n_questions < len(all_questions):
        import random as _random
        _rng = _random.Random(f"{user}:{qid}")
        questions = _rng.sample(all_questions, n_questions)
    else:
        questions = all_questions

    total     = len(questions)
    q_widgets = []

    # Restore per-question state from home dir (best-effort)
    persisted = _load_state(user, qid) if not is_instructor else None

    # ── score bar + completion ─────────────────────────────────────────────
    score_bar  = widgets.HTML()
    finish_out = widgets.Output()

    def _update():
        score    = sum(1 for qw in q_widgets if qw.answered_correctly)
        answered = sum(1 for qw in q_widgets if qw.locked)
        pct      = score / total * 100 if total else 0

        score_bar.value = (
            f'<div style="background:{_C["navy"]};color:{_C["white"]};'
            f'border-radius:8px;padding:10px 18px;margin:8px 0;font-weight:600;">'
            f'Score: {score} / {total} &nbsp;'
            f'<span style="opacity:0.82;">({pct:.0f}%)</span>'
            f'&nbsp;—&nbsp; {answered} of {total} completed'
            f'</div>'
        )

        # Save per-question state to home dir
        if not is_instructor:
            _save_state(user, qid, {
                "quiz_id": qid, "user": user, "timestamp": time.asctime(),
                "score": score, "total": total,
                "questions": [qw.get_state() for qw in q_widgets],
            })

        if answered == total:
            grade_col = (_C["green"] if pct >= 80 else
                         _C["amber"] if pct >= 60 else _C["red"])
            grade_msg = ("Excellent! 🌟"       if pct >= 90 else
                         "Well done! ✅"        if pct >= 80 else
                         "Good effort — review what you missed." if pct >= 60 else
                         "Review the material and speak with your instructor.")
            with finish_out:
                finish_out.clear_output(wait=True)
                display(HTML(
                    f'<div style="background:{grade_col};color:{_C["white"]};'
                    f'border-radius:8px;padding:14px 20px;margin:8px 0;'
                    f'font-weight:700;font-size:1.1em;">'
                    f'🎉 Quiz complete! &nbsp; {score}/{total} ({pct:.0f}%) &nbsp;— {grade_msg}'
                    f'</div>'
                    f'<div style="padding:4px 0;color:{_C["navy"]};font-size:0.92em;">'
                    f'Your score (<b>{score}</b>) has been recorded. '
                    f'Click <b>Submit Quiz</b> in the next cell.'
                    f'</div>'
                ))

    # ── header ─────────────────────────────────────────────────────────────
    att_str = (f"{mxa} attempt per question" if mxa == 1
               else f"{mxa} attempts per question")
    header = widgets.HTML(
        f'<div style="background:{_C["cherry"]};color:{_C["white"]};'
        f'border-radius:10px 10px 0 0;padding:14px 20px;'
        f'font-size:1.2em;font-weight:800;">'
        f'📝 {qid} &nbsp;'
        f'<span style="font-size:0.78em;font-weight:400;opacity:0.9;">'
        f'{total} questions · {att_str} · feedback shown immediately'
        f'</span></div>'
    )

    # ── build questions ────────────────────────────────────────────────────
    for i, q in enumerate(questions):
        init = None
        if persisted and i < len(persisted.get("questions", [])):
            init = persisted["questions"][i]
        qw = _QuestionWidget(i, q, mxa, _update, init)
        q_widgets.append(qw)

    _update()

    display(widgets.VBox(
        [header, score_bar] + [qw.widget for qw in q_widgets] + [finish_out],
        layout=widgets.Layout(width="100%", max_width="820px")
    ))

    # ── result object ──────────────────────────────────────────────────────
    class _Result:
        def __init__(self, qws, n):
            self._qws   = qws
            self._total = n
            self.locked = False
        @property
        def score(self):
            return sum(1 for qw in self._qws if qw.answered_correctly)
        @property
        def total(self):
            return self._total
        def __iter__(self):
            yield self.score
            yield self.total
        def __repr__(self):
            return f"QuizResult({self.score}/{self.total})"

    return _Result(q_widgets, total)
