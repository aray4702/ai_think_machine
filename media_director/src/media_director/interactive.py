"""Interactive terminal mode: the web UI's flow, in the terminal.

    uv run media-director                      # or: media-director start
    uv run media-director start --backend api  # Anthropic API instead of Claude Code

Every step the web UI offers is here: consent, interview, editing the intent,
answering open questions, choosing or mixing a concept, then either making the
poster (automatic) or writing a prompt for your own tool (manual), with
feedback, undo/redo, revise and export.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from .claude_cli import DEFAULT_BACKEND, ClaudeCLIError
from .director import INTERVIEW_QUESTIONS, IntentDraft, InterviewTurn
from .llm import LLMError
from .prompts import TARGETS
from .render import Renderer
from .session import Session

EDITABLE = ["purpose", "audience", "feeling", "personal_detail", "must_include", "avoid"]


class Terminal:
    """Input and output, replaceable in tests."""

    def __init__(self, ask: Callable[[str], str] = input, say: Callable[[str], None] = print,
                 opener: Callable[[Path], None] | None = None):
        self._ask, self.say, self._open = ask, say, opener

    def ask(self, prompt: str, default: str = "") -> str:
        hint = f" [{default}]" if default else ""
        answer = self._ask(f"{prompt}{hint}: ").strip()
        return answer or default

    def confirm(self, prompt: str, default: bool = False) -> bool:
        answer = self.ask(f"{prompt} (y/n)", "y" if default else "n").lower()
        return answer.startswith("y")

    def choose(self, prompt: str, options: list[str], default: int = 0) -> int:
        for i, o in enumerate(options, 1):
            self.say(f"  {i}. {o}")
        while True:
            raw = self.ask(prompt, str(default + 1))
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return int(raw) - 1
            self.say(f"  Please enter a number from 1 to {len(options)}.")

    def open(self, path: Path) -> None:
        if self._open:
            self._open(path)
        elif sys.platform == "darwin" and shutil.which("open"):
            subprocess.run(["open", str(path)], check=False)
        else:
            self.say(f"  Open {path} to see it.")


def _rule(term: Terminal, title: str) -> None:
    term.say("")
    term.say(f"== {title} ==")


def _spent(term: Terminal, s: Session) -> None:
    term.say(f"  (spent ${s.llm.spent:.2f} of ${s.gate.grants[0].limit:.2f})")


def _show_intent(term: Terminal, draft: IntentDraft) -> None:
    term.say(f"  {draft.summary}")
    for k in EDITABLE:
        v = getattr(draft.intent, k)
        term.say(f"  - {k}: {', '.join(v) if isinstance(v, list) else v}")


def _edit_intent(term: Terminal, draft: IntentDraft) -> None:
    while True:
        field = term.ask("Edit a field? Type its name, or press Enter to continue").lower()
        if not field:
            return
        if field not in EDITABLE:
            term.say(f"  Fields: {', '.join(EDITABLE)}")
            continue
        current = getattr(draft.intent, field)
        if isinstance(current, list):
            value = term.ask(f"New {field} (comma-separated)", ", ".join(current))
            setattr(draft.intent, field, [x.strip() for x in value.split(",") if x.strip()])
        else:
            setattr(draft.intent, field, term.ask(f"New {field}", current))


def _show_outcome(term: Terminal, s: Session, rendered, crit, plan) -> None:
    term.say(f"  Render: {s.dir / s.renders[-1]}")
    if rendered.defects:
        term.say(f"  Automatic checks: {len(rendered.defects)} defect(s)")
    term.say(f"  Stopped: {plan.reason}")
    for x in crit.strengths:
        term.say(f"  + {x}")
    for i in crit.issues:
        term.say(f"  - [{i.severity}] {i.part}: {i.problem}")
    for q in plan.ask + plan.revise_concept:
        term.say(f"  ? {q}")
    _spent(term, s)


def _auto(term: Terminal, s: Session, rounds: int) -> None:
    _rule(term, "Making the poster")
    term.say("  This takes a few minutes...")
    with Renderer() as r:
        first = s.produce(r)
        result = s.refine(r, first, max_rounds=rounds)
        _show_outcome(term, s, *result)
        term.open(s.dir / s.renders[-1])
        while True:
            action = term.ask("[f]eedback, [u]ndo, [r]edo, [o]pen render, [e]xport, [q]uit", "q").lower()[:1]
            try:
                if action == "f":
                    text = term.ask("Your feedback or answers")
                    if text:
                        term.say("  Refining...")
                        result = s.feedback(r, text, max_rounds=rounds)
                        _show_outcome(term, s, *result)
                        term.open(s.dir / s.renders[-1])
                elif action in ("u", "r"):
                    (s.undo if action == "u" else s.redo)(r)
                    term.say(f"  Now at version {s.timeline.cursor + 1} of {len(s.timeline.versions)}: "
                             f"{s.timeline.state.note}")
                    term.open(s.dir / s.renders[-1])
                elif action == "o":
                    term.open(s.dir / s.renders[-1])
                elif action == "e":
                    dest = Path(term.ask("Export to folder", str(s.dir.parent.parent / "exports")))
                    if term.confirm(f"Export is irreversible: copy the poster and its provenance to {dest}?"):
                        term.say(f"  Exported: {s.export(dest, approved=True)}")
                elif action == "q":
                    return
            except (LLMError, ClaudeCLIError, PermissionError) as err:
                term.say(f"  Could not do that: {err}")


def _manual(term: Terminal, s: Session, medium: str) -> None:
    targets = [t for t in TARGETS.values() if medium in t.media]
    while True:
        _rule(term, "Prompt for your tool")
        t = targets[term.choose("Your tool", [t.label for t in targets])]
        fp, path = s.manual_prompt(t.name)
        term.say(path.read_text())
        _spent(term, s)
        while True:
            action = term.ask("[c]opy prompt, [r]evise from your result, [t]ool change, [q]uit", "q").lower()[:1]
            try:
                if action == "c":
                    if shutil.which("pbcopy"):
                        subprocess.run(["pbcopy"], input=fp.prompt, text=True, check=False)
                        term.say("  Copied to the clipboard.")
                    else:
                        term.say(fp.prompt)
                elif action == "r":
                    image = Path(term.ask("Path to the image your tool made").strip("'\""))
                    if not image.exists():
                        term.say("  That file does not exist.")
                        continue
                    note = term.ask("What do you think of it? (optional)")
                    term.say("  Judging it...")
                    rev, path = s.revise(image.read_bytes(), note)
                    for x in rev.what_works:
                        term.say(f"  + {x}")
                    for x in rev.what_misses_the_intent:
                        term.say(f"  - {x}")
                    fp = rev.revised
                    term.say(path.read_text())
                    _spent(term, s)
                elif action == "t":
                    break
                elif action == "q":
                    return
            except (LLMError, ClaudeCLIError, PermissionError, ValueError) as err:
                term.say(f"  Could not do that: {err}")


def run(workspace: Path, backend: str = DEFAULT_BACKEND, term: Terminal | None = None, client=None) -> Session | None:
    term = term or Terminal()
    _rule(term, "Media Director")
    term.say(f"  Backend: {'Claude Code CLI (your Claude Code login)' if backend == 'claude-code' else 'Anthropic API'}")
    if not term.confirm("Your answers, and any image you give, are sent to Claude for this session. Agree?"):
        term.say("  Nothing was sent.")
        return None
    while True:
        try:
            budget = float(term.ask("Spending limit for this session in US$", "3"))
            if 0 < budget <= 20:
                break
        except ValueError:
            pass
        term.say("  Please enter an amount between 0 and 20.")
    s = Session(workspace, budget=budget, client=client, backend=backend)
    s.consent_to_send()

    medium = ["poster", "slides"][term.choose("What are you making?", ["Poster", "Slides (manual mode)"])]
    mode = "manual" if medium == "slides" else \
        ["auto", "manual"][term.choose("How should it be made?",
                                       ["Automatic: the director makes the poster",
                                        "Manual: the director writes a prompt for your own tool"])]
    try:
        _rule(term, "Interview")
        turns = []
        for q in INTERVIEW_QUESTIONS:
            a = term.ask(q)
            if a:
                turns.append(InterviewTurn(question=q, answer=a))
        if not turns:
            term.say("  No answers, so nothing to make.")
            return s
        term.say("  Reading your answers...")
        draft = s.draft_intent(medium, turns)

        _rule(term, "Your intent")
        _show_intent(term, draft)
        _edit_intent(term, draft)
        answers = []
        for q in draft.intent.open_questions:
            a = term.ask(f"{q} (Enter to skip)")
            if a:
                answers.append((q, a))
        draft.intent.open_questions = []
        s.confirm_intent(draft, answers)

        while True:
            _rule(term, "Concepts")
            term.say("  Proposing concepts...")
            concepts = s.concepts()
            for i, c in enumerate(concepts, 1):
                term.say(f"  {i}. {c.title}\n     {c.idea}\n     Personal: {c.why_personal}\n"
                         f"     Mood: {c.mood} | Palette: {' '.join(c.palette)}")
            raw = term.ask("Choose a concept by number, or [n]ew concepts", "1")
            if raw.lower().startswith("n"):
                continue
            if raw.isdigit() and 1 <= int(raw) <= len(concepts):
                break
            term.say("  Please choose one of the numbers.")
        note = term.ask("Anything to change or mix in? (optional)")
        s.choose(concepts[int(raw) - 1], note=note)
        _spent(term, s)

        if mode == "auto":
            rounds = int(term.ask("Refinement rounds (1-3)", "2") or 2)
            _auto(term, s, max(1, min(3, rounds)))
        else:
            _manual(term, s, medium)
    except (LLMError, ClaudeCLIError, PermissionError) as err:
        term.say(f"  Stopped: {err}")
    term.say(f"  Session saved in {s.dir}")
    return s
