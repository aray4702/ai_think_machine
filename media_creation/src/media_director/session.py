"""One creative session: from interview to an exported poster.

The session owns the pieces of One Loop for this piece: W (pinned), the gate,
the LLM client, the asset store, the timeline, the episodic log and the
renderer. Every step is saved to the session folder so it can be inspected,
undone, or resumed.
"""

from __future__ import annotations

import json
import shutil
import time
import uuid
from pathlib import Path

from . import agents
from .controller import Plan, plan_fixes
from .director import (Briefs, Concept, Critique, IntentDraft, InterviewTurn, adopt_intent,
                       compile_briefs, critique, diverge, extract_intent)
from .eventlog import EventLog
from .gates import Action, Gate, Grant
from .llm import ESTIMATE, LLM, PERSONAL_SCOPE
from .render import Rendered, Renderer
from .sources import Source
from .timeline import AssetStore, Part, Timeline
from .tools import assemble
from .working import Goal, WorkingState

ROUND_COST = ESTIMATE["claude-opus-5-5"] + 3 * ESTIMATE["claude-sonnet-5-5"]


class Session:
    def __init__(self, workspace: Path, budget: float, client=None, session_id: str | None = None):
        self.id = session_id or time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
        self.dir = Path(workspace) / "sessions" / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.gate = Gate([
            Grant(Action.SPEND, limit=budget),
            Grant(Action.WRITE_WORKSPACE, scope=str(self.dir)),
            Grant(Action.SEND_PERSONAL, scope=PERSONAL_SCOPE),
            Grant(Action.EXPORT),
        ])
        self.llm = LLM(gate=self.gate, client=client)
        self.w = WorkingState(envelope=self.gate.envelope())
        self.store = AssetStore(Path(workspace) / "assets")
        self.timeline = Timeline("poster")
        self.log = EventLog(self.dir / "episodes.jsonl")
        self.concept: Concept | None = None
        self.briefs: Briefs | None = None
        self.renders: list[str] = []

    # --- consent and intent ------------------------------------------------------
    def consent_to_send(self) -> None:
        """The person agreed that their answers may be sent to Claude this session."""
        self.gate.approve(Action.SEND_PERSONAL, PERSONAL_SCOPE, once=False)
        self.log.add("consent", salience=["person"], scope=PERSONAL_SCOPE)

    def draft_intent(self, medium: str, turns: list[InterviewTurn]) -> IntentDraft:
        draft = extract_intent(self.llm, medium, turns)
        self.log.add("intent_draft", draft=draft.model_dump())
        return draft

    def confirm_intent(self, draft: IntentDraft) -> None:
        adopt_intent(self.w, draft)
        self.w.push(Goal(id="piece", description=f"A {draft.intent.medium} for: {draft.intent.purpose}",
                         test="The person approves it for export"))
        self.log.add("intent_confirmed", salience=["person"], summary=draft.summary)
        self._save()

    # --- concepts ------------------------------------------------------------------
    def concepts(self, n: int = 4, style_profile: str = "") -> list[Concept]:
        out = diverge(self.llm, self.w, n, style_profile)
        self.log.add("concepts", concepts=[c.model_dump() for c in out])
        return out

    def choose(self, concept: Concept, note: str = "") -> None:
        self.concept = concept
        self.log.add("choice", salience=["person", "taste"], concept=concept.model_dump(), note=note)

    # --- production -------------------------------------------------------------------
    def produce(self, renderer: Renderer) -> Rendered:
        assert self.concept, "choose a concept first"
        self.briefs = compile_briefs(self.llm, self.w, self.concept)
        self.log.add("briefs", briefs=self.briefs.model_dump())
        for role in ("copy", "illustration", "layout"):
            self._generate(role)
        return self.render(renderer, note="first draft")

    def _generate(self, role: str, note: str = "") -> None:
        b = self.briefs
        if role == "copy":
            brief = b.copy_brief
            if note:
                brief = brief.model_copy(update={"content": brief.content + "\nRevision: " + note})
            asset_id, _ = agents.write_copy(self.llm, self.store, brief)
        elif role == "illustration":
            brief = b.illustration
            if note:
                brief = brief.model_copy(update={"style": brief.style + "\nRevision: " + note})
            asset_id, _ = agents.draw_illustration(self.llm, self.store, brief)
        else:
            brief = b.layout
            if note:
                brief = brief.model_copy(update={"composition": brief.composition + "\nRevision: " + note})
            asset_id, _ = agents.lay_out(self.llm, self.store, brief)
        self.timeline.set_part(Part(id=role, role=role, asset_id=asset_id),
                               note=f"{'regenerate' if note else 'generate'} {role}")
        self.log.add("generate", part=role, asset=asset_id, revision=note or None)

    def html(self) -> str:
        return assemble(self.timeline.state, self.store)

    def copy_texts(self) -> dict[str, str]:
        parts = {p.role: p for p in self.timeline.state.parts}
        if "copy" not in parts:
            return {}
        texts = json.loads(self.store.get(parts["copy"].asset_id))
        for op in parts["copy"].edits:
            if op.tool == "set_text":
                texts[op.args["slot"]] = op.args["text"]
        return texts

    def render(self, renderer: Renderer, note: str = "") -> Rendered:
        r = renderer.render(self.html())
        n = len(self.renders)
        png = self.dir / f"render-{n:02d}.png"
        png.write_bytes(r.png)
        (self.dir / f"render-{n:02d}.html").write_text(self.html())
        self.renders.append(png.name)
        self.log.add("render", file=png.name, note=note, defects=[d.model_dump() for d in r.defects],
                     salience=["defect"] if r.defects else [])
        self._save()
        return r

    # --- critique and refinement ---------------------------------------------------------
    def refine(self, renderer: Renderer, rendered: Rendered, max_rounds: int = 3) -> tuple[Rendered, Critique, Plan]:
        round_no = 0
        while True:
            c = critique(self.llm, self.w, self.concept, rendered.png, rendered.defects, self.copy_texts())
            budget_left = self._budget_left()
            plan = plan_fixes(c, round_no, max_rounds, budget_left, ROUND_COST)
            self.log.add("critique", round=round_no, critique=c.model_dump(),
                         plan={"edits": [(p, op.model_dump()) for p, op in plan.edits],
                               "regenerate": plan.regenerate, "ask": plan.ask,
                               "revise_concept": plan.revise_concept, "stop": plan.stop,
                               "reason": plan.reason})
            if plan.stop:
                return rendered, c, plan
            for part, op in plan.edits:
                self.timeline.edit(part, op, note=f"K: {op.tool}")
            for part, note in plan.regenerate.items():
                self._generate(part, note)
            rendered = self.render(renderer, note=f"round {round_no + 1}")
            round_no += 1

    def _budget_left(self) -> float:
        g = next(g for g in self.gate.grants if g.action is Action.SPEND)
        return (g.limit or 0) - g.used

    # --- export (irreversible) -------------------------------------------------------------
    def export(self, dest: Path, approved: bool) -> Path:
        dest = Path(dest)
        if approved:
            self.gate.approve(Action.EXPORT, str(dest))
        d = self.gate.decide(Action.EXPORT, Source.DIRECTOR, scope=str(dest))
        if not d.allowed:
            raise PermissionError(d.reason)
        dest.mkdir(parents=True, exist_ok=True)
        last = self.renders[-1]
        shutil.copy(self.dir / last, dest / f"{self.id}.png")
        (dest / f"{self.id}.html").write_text(self.html())
        provenance = {
            "session": self.id, "generated_by": "AI (Claude) directed by the person",
            "parts": [{"role": p.role, "asset": p.asset_id, **{k: v for k, v in self.store.meta(p.asset_id).items()
                                                                if k in ("agent", "model", "brief_sha")}}
                      for p in self.timeline.state.parts],
            "edits": [op.model_dump() for p in self.timeline.state.parts for op in p.edits],
        }
        (dest / f"{self.id}.provenance.json").write_text(json.dumps(provenance, indent=2))
        self.log.add("export", salience=["person", "irreversible"], dest=str(dest))
        return dest / f"{self.id}.png"

    # --- persistence ------------------------------------------------------------------------
    def _save(self) -> None:
        (self.dir / "working_state.json").write_text(self.w.model_dump_json(indent=2))
        (self.dir / "timeline.json").write_text(self.timeline.to_json())
        (self.dir / "costs.json").write_text(json.dumps(
            {"spent": self.llm.spent, "calls": self.llm.calls, "gate_log": self.gate.log}, indent=2))
