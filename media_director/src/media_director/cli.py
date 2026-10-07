"""Command-line interface.

Interactive (the full flow in the terminal; the default):

    uv run media-director
    uv run media-director start --backend claude-code

Automatic mode - the director runs specialist agents and renders the poster:

    uv run media-director poster --answers answers.json --budget 3 --consent

Manual mode - the director writes the final prompt for your own tool:

    uv run media-director prompt --answers answers.json --target midjourney --consent
    uv run media-director revise --session <id> --image result.png --note "too dark" --consent

Web UI (both modes, in the browser):

    uv run media-director serve

answers.json holds the interview answers in order, plus optional "concept"
(index of the concept to pick) and "medium" ("poster" or "slides").
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .director import INTERVIEW_QUESTIONS, InterviewTurn
from .claude_cli import BACKENDS
from .prompts import TARGETS
from .render import Renderer
from .session import Session


def _backend(p: argparse.ArgumentParser) -> None:
    p.add_argument("--backend", choices=BACKENDS, default="api",
                   help="api: Anthropic API (per-token billing); claude-code: the `claude` CLI and its login")


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--budget", type=float, default=3.0, help="spending limit in US dollars")
    p.add_argument("--workspace", type=Path, default=Path("workspace"))
    _backend(p)
    p.add_argument("--consent", action="store_true",
                   help="I agree that my answers and images may be sent to Claude for this session")


def _start(args) -> Session:
    """Interview -> confirmed intent -> concepts -> the chosen concept."""
    spec = json.loads(args.answers.read_text())
    s = Session(args.workspace, budget=args.budget, backend=args.backend)
    s.consent_to_send()
    medium = spec.get("medium", "poster")
    turns = [InterviewTurn(question=q, answer=a) for q, a in zip(INTERVIEW_QUESTIONS, spec["answers"])]
    draft = s.draft_intent(medium, turns)
    print("Intent:", draft.summary)
    if draft.intent.open_questions:
        print("Open questions (answer them in the web UI later):", *draft.intent.open_questions, sep="\n- ")
    s.confirm_intent(draft)
    concepts = s.concepts()
    for i, c in enumerate(concepts):
        print(f"[{i}] {c.title}: {c.idea}")
    pick = int(spec.get("concept", 0))
    s.choose(concepts[pick], note="picked in CLI")
    print(f"Session: {s.id}")
    return s


def main() -> None:
    ap = argparse.ArgumentParser(prog="media-director")
    sub = ap.add_subparsers(dest="cmd")
    st = sub.add_parser("start", help="interactive: the whole flow in the terminal (default)")
    st.add_argument("--workspace", type=Path, default=Path("workspace"))
    _backend(st)
    p = sub.add_parser("poster", help="automatic mode: make one poster end to end")
    p.add_argument("--answers", type=Path, required=True)
    p.add_argument("--rounds", type=int, default=2)
    _common(p)
    m = sub.add_parser("prompt", help="manual mode: write the final prompt for your own tool")
    m.add_argument("--answers", type=Path, required=True)
    m.add_argument("--target", choices=sorted(TARGETS), required=True)
    _common(m)
    r = sub.add_parser("revise", help="manual mode: judge your tool's result and revise the prompt")
    r.add_argument("--session", required=True)
    r.add_argument("--image", type=Path, required=True, help="the image your tool produced (PNG, JPEG, WebP or GIF)")
    r.add_argument("--note", default="", help="what you think of the result")
    _common(r)
    sub.add_parser("targets", help="list the tools manual mode can write prompts for")
    w = sub.add_parser("serve", help="open the web UI on 127.0.0.1")
    w.add_argument("--port", type=int, default=8765)
    w.add_argument("--workspace", type=Path, default=Path("workspace"))
    _backend(w)
    args = ap.parse_args()

    if args.cmd in (None, "start"):
        from .interactive import run
        run(getattr(args, "workspace", Path("workspace")), backend=getattr(args, "backend", "api"))
        return
    if args.cmd == "serve":
        from .server import serve
        serve(args.workspace, args.port, backend=args.backend)
        return
    if args.cmd == "targets":
        for t in TARGETS.values():
            print(f"{t.name:18} {t.label}  ({', '.join(t.media)})")
        return
    if not args.consent:
        raise SystemExit("Your answers and images are sent to Claude. Re-run with --consent to agree.")

    if args.cmd == "prompt":
        s = _start(args)
        fp, path = s.manual_prompt(args.target)
        print("\n" + path.read_text())
        print(f"Saved to {path}. Spent ${s.llm.spent:.2f}.")
        print(f"After generating, run: media-director revise --session {s.id} --image result.png --consent")
        return
    if args.cmd == "revise":
        s = Session.load(args.workspace, args.session, budget=args.budget, backend=args.backend)
        s.consent_to_send()
        rev, path = s.revise(args.image.read_bytes(), args.note)
        print("Works:", *rev.what_works, sep="\n- ")
        print("Misses the intent:", *rev.what_misses_the_intent, sep="\n- ")
        print("\n" + path.read_text())
        print(f"Saved to {path}. Spent ${s.llm.spent:.2f}.")
        return

    s = _start(args)
    with Renderer() as r:
        first = s.produce(r)
        print(f"First draft: {len(first.defects)} automatic-check defects")
        final, crit, plan = s.refine(r, first, max_rounds=args.rounds)
    print(f"Stopped: {plan.reason}")
    for issue in crit.issues:
        print(f"- [{issue.severity}] {issue.part}: {issue.problem} -> {issue.fix}")
    print(f"Spent ${s.llm.spent:.2f}; renders in {s.dir}")


if __name__ == "__main__":
    main()
