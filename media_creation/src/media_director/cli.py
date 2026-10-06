"""Command-line runner for one poster, end to end, without the web UI.

    uv run media-director poster --answers answers.json --budget 3 --consent

answers.json holds the interview answers in order, plus optional "concept"
(index of the concept to pick). The web UI replaces this in a later step.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .director import INTERVIEW_QUESTIONS, InterviewTurn
from .render import Renderer
from .session import Session


def main() -> None:
    ap = argparse.ArgumentParser(prog="media-director")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("poster", help="make one poster end to end")
    p.add_argument("--answers", type=Path, required=True)
    p.add_argument("--budget", type=float, default=3.0, help="spending limit in US dollars")
    p.add_argument("--workspace", type=Path, default=Path("workspace"))
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--consent", action="store_true",
                   help="I agree that my answers may be sent to Claude for this session")
    args = ap.parse_args()

    spec = json.loads(args.answers.read_text())
    if not args.consent:
        raise SystemExit("Your answers are sent to Claude. Re-run with --consent to agree.")
    s = Session(args.workspace, budget=args.budget)
    s.consent_to_send()
    turns = [InterviewTurn(question=q, answer=a) for q, a in zip(INTERVIEW_QUESTIONS, spec["answers"])]
    draft = s.draft_intent("poster", turns)
    print("Intent:", draft.summary)
    if draft.intent.open_questions:
        print("Open questions (answer them in the web UI later):", *draft.intent.open_questions, sep="\n- ")
    s.confirm_intent(draft)

    concepts = s.concepts()
    for i, c in enumerate(concepts):
        print(f"[{i}] {c.title}: {c.idea}")
    pick = int(spec.get("concept", 0))
    s.choose(concepts[pick], note="picked in CLI")

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
