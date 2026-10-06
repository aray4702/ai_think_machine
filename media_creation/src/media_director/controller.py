"""Controller K: hand-coded rules, every decision logged.

For each issue K picks the cheapest fix that can work - edit before
regenerate, regenerate a part before revising the concept, and ask the person
when the problem is theirs to decide. It stops when nothing serious remains,
when rounds run out, or when the budget is too low for another round.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .director import Critique, Issue
from .tools import EditError, validate

COST_ORDER = ["edit", "regenerate_copy", "regenerate_illustration", "regenerate_layout",
              "revise_concept", "ask_person"]


@dataclass
class Plan:
    edits: list[tuple[str, object]] = field(default_factory=list)  # (part role, EditOp)
    regenerate: dict[str, str] = field(default_factory=dict)  # part -> brief note
    ask: list[str] = field(default_factory=list)
    revise_concept: list[str] = field(default_factory=list)
    stop: bool = False
    reason: str = ""


TEXT_PART_TOOLS = {"set_text"}


def plan_fixes(c: Critique, round_no: int, max_rounds: int, budget_left: float,
               round_cost: float) -> Plan:
    serious = [i for i in c.issues if i.severity in ("high", "medium")]
    if c.serves_intent and not serious:
        return Plan(stop=True, reason="serves the intent; no serious issues")
    if round_no >= max_rounds:
        return Plan(stop=True, reason=f"reached {max_rounds} rounds; hand to the person")
    if budget_left < round_cost:
        return Plan(stop=True, reason="budget too low for another round; hand to the person")

    plan = Plan()
    for issue in sorted(serious, key=lambda i: COST_ORDER.index(i.fix)):
        _route(plan, issue)
    if plan.ask:
        plan.stop, plan.reason = True, "a question only the person can answer"
    elif plan.revise_concept:
        plan.stop, plan.reason = True, "the concept itself needs revising; ask the person"
    return plan


def _route(plan: Plan, issue: Issue) -> None:
    if issue.fix == "edit":
        valid = []
        for op in issue.edits:
            try:
                valid.append(validate(op))
            except EditError:
                continue
        if valid:
            for op in valid:
                part = "copy" if op.tool in TEXT_PART_TOOLS else "layout"
                plan.edits.append((part, op))
            return
        # An edit fix with no usable operations escalates to regenerating the part.
        issue = issue.model_copy(update={"fix": "regenerate_layout"
                                         if issue.part not in ("illustration",) else "regenerate_illustration"})
    if issue.fix.startswith("regenerate_"):
        part = issue.fix.removeprefix("regenerate_")
        note = plan.regenerate.get(part, "")
        plan.regenerate[part] = (note + "\n" if note else "") + (issue.brief_note or issue.problem)
    elif issue.fix == "revise_concept":
        plan.revise_concept.append(issue.problem)
    elif issue.fix == "ask_person":
        plan.ask.append(issue.problem)
