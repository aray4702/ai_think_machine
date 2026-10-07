"""Working state W: the person's intent, the goal stack, standing constraints
and the permission envelope.

W is pinned: it is rendered in full into every director call and never
summarized away, so context compaction cannot drop a constraint (the
governance-decay failure). Only the person can change the intent or the
standing constraints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .sources import Tagged


class Intent(BaseModel):
    """What the piece is for, captured from the person's own words."""

    medium: str = Field(description="poster or slides")
    purpose: str = Field(description="What the piece is for")
    audience: str = Field(description="Who it is for")
    feeling: str = Field(description="What the audience should feel, and when")
    personal_detail: str = Field(description="One concrete detail from the person's life behind the piece")
    must_include: list[str] = Field(default_factory=list, description="Text or elements the person requires")
    avoid: list[str] = Field(default_factory=list, description="Anti-references: what the person does not want")
    open_questions: list[str] = Field(
        default_factory=list, description="What is still unclear and should be asked"
    )


class Goal(BaseModel):
    id: str
    description: str
    test: str = Field(description="The TOTE test: how to tell the goal is met")
    status: str = "open"  # open | done | failed


class GoalGateError(PermissionError):
    """Raised when a source without authority tries to change the goal."""


class WorkingState(BaseModel):
    intent: Intent | None = None
    goals: list[Goal] = Field(default_factory=list)  # a stack; last is current
    constraints: list[str] = Field(default_factory=list)  # standing, from the person
    envelope: list[str] = Field(default_factory=list)  # human-readable grant summary

    # --- goal gate -----------------------------------------------------
    def set_intent(self, intent: Intent, provenance: Tagged) -> None:
        if not provenance.can_set_goal:
            raise GoalGateError(f"{provenance.source.value} cannot set the intent")
        self.intent = intent

    def add_constraint(self, constraint: str, provenance: Tagged) -> None:
        if not provenance.can_set_goal:
            raise GoalGateError(f"{provenance.source.value} cannot add constraints")
        if constraint not in self.constraints:
            self.constraints.append(constraint)

    # --- goal stack ----------------------------------------------------
    def push(self, goal: Goal) -> None:
        self.goals.append(goal)

    def pop(self, status: str = "done") -> Goal:
        goal = self.goals.pop()
        goal.status = status
        return goal

    @property
    def current(self) -> Goal | None:
        return self.goals[-1] if self.goals else None

    # --- pinning -------------------------------------------------------
    def pinned(self) -> str:
        """The block recited in every director call. Never compacted."""
        lines = ["<working_state pinned=\"true\">"]
        if self.intent:
            lines.append("Intent (set by the person):")
            lines.append(self.intent.model_dump_json(indent=2))
        if self.constraints:
            lines.append("Standing constraints (set by the person):")
            lines += [f"- {c}" for c in self.constraints]
        if self.goals:
            lines.append("Goal stack (current last):")
            lines += [f"- [{g.status}] {g.description} | test: {g.test}" for g in self.goals]
        if self.envelope:
            lines.append("Permission envelope:")
            lines += [f"- {e}" for e in self.envelope]
        lines.append("</working_state>")
        return "\n".join(lines)
