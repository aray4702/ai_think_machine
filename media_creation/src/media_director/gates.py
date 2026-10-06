"""Grants (R9) and the action gate (R1).

Default deny: an action runs only if an explicit grant covers it. The gate
asks two separate questions - is it allowed (a grant) and is it wise
(reversibility) - and irreversible actions need the person's approval each
time, even when granted. Requests carry the authority of their source, so a
specialist agent or a tool cannot request an action at all.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

from .sources import ACTION_REQUESTERS, Source


class Action(str, Enum):
    SPEND = "spend"  # model calls, in US dollars
    WRITE_WORKSPACE = "write_workspace"  # assets and timeline in the workspace
    SEND_PERSONAL = "send_personal"  # personal material sent to a model (a data flow)
    EXPORT = "export"  # copy a finished piece out of the workspace


class Reversibility(str, Enum):
    REVERSIBLE = "reversible"
    COMPENSABLE = "compensable"
    IRREVERSIBLE = "irreversible"


REVERSIBILITY = {
    Action.WRITE_WORKSPACE: Reversibility.REVERSIBLE,  # versioned, undoable
    Action.SPEND: Reversibility.COMPENSABLE,  # money is gone, but bounded by budget
    Action.SEND_PERSONAL: Reversibility.IRREVERSIBLE,  # disclosure cannot be undone
    Action.EXPORT: Reversibility.IRREVERSIBLE,  # publishing, in effect
}


@dataclass
class Grant:
    action: Action
    scope: str = "*"  # a path prefix, a model name, or "*"
    limit: float | None = None  # for SPEND: dollars
    expires_at: float | None = None
    granted_by: str = "person"
    used: float = 0.0

    def covers(self, action: Action, scope: str, now: float) -> bool:
        if action != self.action:
            return False
        if self.expires_at is not None and now > self.expires_at:
            return False
        return self.scope == "*" or scope.startswith(self.scope)

    def describe(self) -> str:
        parts = [self.action.value, f"scope={self.scope}"]
        if self.limit is not None:
            parts.append(f"limit=${self.limit:.2f} (used ${self.used:.2f})")
        return " ".join(parts)


@dataclass
class Decision:
    allowed: bool
    needs_approval: bool = False
    permission_gap: bool = False
    reason: str = ""
    grant: Grant | None = None


@dataclass
class Gate:
    grants: list[Grant] = field(default_factory=list)
    log: list[dict] = field(default_factory=list)

    def grant(self, g: Grant) -> None:
        self.grants.append(g)

    def envelope(self) -> list[str]:
        return [g.describe() for g in self.grants]

    def decide(
        self,
        action: Action,
        requester: Source,
        scope: str = "*",
        amount: float = 0.0,
        now: float | None = None,
    ) -> Decision:
        now = time.time() if now is None else now
        if requester not in ACTION_REQUESTERS:
            d = Decision(False, reason=f"{requester.value} has no authority to request actions")
        else:
            g = next((g for g in self.grants if g.covers(action, scope, now)), None)
            if g is None:
                d = Decision(False, permission_gap=True, reason=f"no grant for {action.value} on {scope}")
            elif g.limit is not None and g.used + amount > g.limit:
                d = Decision(False, permission_gap=True, grant=g,
                             reason=f"{action.value} would exceed limit ${g.limit:.2f}")
            elif REVERSIBILITY[action] is Reversibility.IRREVERSIBLE:
                d = Decision(False, needs_approval=True, grant=g,
                             reason=f"{action.value} is irreversible and needs the person's approval")
            else:
                d = Decision(True, grant=g, reason="granted")
        self.log.append({"t": now, "action": action.value, "scope": scope, "amount": amount,
                         "requester": requester.value, "allowed": d.allowed,
                         "needs_approval": d.needs_approval, "gap": d.permission_gap, "reason": d.reason})
        return d

    def charge(self, decision: Decision, amount: float) -> None:
        """Record spending against the grant that allowed it."""
        if decision.grant is not None:
            decision.grant.used += amount

    def narrowed(self, actions: set[Action]) -> "Gate":
        """A gate for a delegate: a subset of this gate's grants, never more."""
        return Gate(grants=[g for g in self.grants if g.action in actions])
