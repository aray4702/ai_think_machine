import json
from types import SimpleNamespace

import pytest

from media_director.agents import Copy
from media_director.controller import plan_fixes
from media_director.director import Briefs, Concept, Concepts, Critique, IntentDraft, Issue, InterviewTurn
from media_director.gates import Action
from media_director.llm import NeedsApproval
from media_director.render import Renderer
from media_director.session import Session
from media_director.timeline import AssetStore, EditOp, Part, PieceState
from media_director.tools import EditError, assemble, extract, sanitize, validate
from media_director.working import Intent

LAYOUT = """<!doctype html><html><head><style>
:root { --bg: #102030; --fg: #f5efe6; --accent: #f0a030; --muted: #8899aa;
        --font-head: Georgia, serif; --font-body: Helvetica, sans-serif; }
body { margin: 0; width: 1080px; height: 1350px; background: var(--bg); color: var(--fg); }
[data-slot="illustration"] { position: absolute; left: 140px; top: 140px; width: 800px; height: 800px; }
[data-slot="illustration"] svg { width: 100%; height: 100%; }
[data-slot="headline"] { position: absolute; left: 80px; top: 1000px; width: 920px; height: 120px;
  font: 700 72px var(--font-head); margin: 0; overflow: hidden; }
[data-slot="subline"] { position: absolute; left: 80px; top: 1140px; width: 920px; height: 60px;
  font: 32px var(--font-body); margin: 0; overflow: hidden; }
</style></head><body>
<div data-slot="illustration"></div><h1 data-slot="headline"></h1><p data-slot="subline"></p>
<script>alert(1)</script></body></html>"""
SVG = '<svg viewBox="0 0 100 100" onload="evil()"><circle cx="50" cy="50" r="40" fill="#f0a030"/></svg>'


def piece(tmp_path, copy=None, edits=()):
    store = AssetStore(tmp_path / "assets")
    state = PieceState(parts=[
        Part(id="layout", role="layout", asset_id=store.put(LAYOUT.encode(), ".html"), edits=list(edits)),
        Part(id="copy", role="copy", asset_id=store.put(json.dumps(copy or {"headline": "Ten Orbits",
                                                                           "subline": "for Mira"}).encode(), ".json")),
        Part(id="illustration", role="illustration", asset_id=store.put(SVG.encode(), ".svg")),
    ])
    return state, store


# --- tools ---------------------------------------------------------------------------

def test_assemble_fills_slots_sanitizes_and_applies_edits(tmp_path):
    state, store = piece(tmp_path, edits=[EditOp(tool="set_var", args={"name": "accent", "value": "#e05050"}),
                                          EditOp(tool="style", args={"slot": "headline", "css": "font-size: 60px"})])
    html = assemble(state, store)
    assert "Ten Orbits" in html and "for Mira" in html and "<circle" in html
    assert "<script" not in html and "onload" not in html
    assert "--accent: #e05050" in html and 'font-size: 60px' in html


def test_text_edits_escape_markup(tmp_path):
    state, store = piece(tmp_path)
    state.parts[1].edits.append(EditOp(tool="set_text", args={"slot": "headline", "text": "<b>hi</b>"}))
    assert "&lt;b&gt;hi&lt;/b&gt;" in assemble(state, store)


def test_validate_rejects_injection():
    for op in (EditOp(tool="style", args={"slot": "headline", "css": "} body { display:none"}),
               EditOp(tool="set_var", args={"name": "accent", "value": "red;}</style><script>"}),
               EditOp(tool="exec", args={})):
        with pytest.raises(EditError):
            validate(op)


def test_sanitize_and_extract():
    assert "javascript:" not in sanitize('<a href="javascript:alert(1)">x</a>')
    assert "<iframe" not in sanitize('<iframe src="x"></iframe>')
    assert "evil.com" not in sanitize('<link rel="stylesheet" href="https://evil.com/a.css">')
    assert "fonts.googleapis.com" in sanitize('<link href="https://fonts.googleapis.com/css2?family=Lora">')
    assert extract("Here you go:\n<svg viewBox='0 0 1 1'></svg>\nDone", "svg").startswith("<svg")


# --- rendering in Chrome -------------------------------------------------------------

def test_render_and_checks(tmp_path):
    state, store = piece(tmp_path)
    with Renderer() as r:
        ok = r.render(assemble(state, store))
        assert ok.png[:8] == b"\x89PNG\r\n\x1a\n"
        assert ok.defects == []
        long = "An extremely long headline that cannot possibly fit in a single 120 pixel tall box at 72px"
        bad_state, _ = piece(tmp_path, copy={"headline": long, "subline": ""},
                             edits=[EditOp(tool="set_var", args={"name": "fg", "value": "#1a2a3a"})])
        bad = r.render(assemble(bad_state, store))
    kinds = {(d.slot, d.kind) for d in bad.defects}
    assert ("headline", "overflow") in kinds
    assert ("headline", "low_contrast") in kinds
    assert ("subline", "empty") in kinds


# --- controller K ---------------------------------------------------------------------

def crit(*issues, serves=False):
    return Critique(serves_intent=serves, strengths=[], issues=list(issues))


def test_k_stops_when_done():
    assert plan_fixes(crit(serves=True), 0, 3, 5.0, 1.0).stop


def test_k_prefers_edits_and_escalates_empty_edits():
    edit = Issue(part="headline", problem="too big", severity="high", fix="edit",
                 edits=[EditOp(tool="style", args={"slot": "headline", "css": "font-size: 56px"})])
    empty = Issue(part="illustration", problem="generic", severity="medium", fix="edit")
    plan = plan_fixes(crit(edit, empty), 0, 3, 5.0, 1.0)
    assert plan.edits[0][0] == "layout" and plan.edits[0][1].tool == "style"
    assert "illustration" in plan.regenerate and not plan.stop


def test_k_asks_person_and_respects_budget():
    ask = Issue(part="whole", problem="which name to use?", severity="high", fix="ask_person")
    assert plan_fixes(crit(ask), 0, 3, 5.0, 1.0).stop
    # with a fixable issue too, K applies the fix first and then asks
    edit = Issue(part="headline", problem="too big", severity="high", fix="edit",
                 edits=[EditOp(tool="style", args={"slot": "headline", "css": "font-size: 56px"})])
    both = plan_fixes(crit(ask, edit), 0, 3, 5.0, 1.0)
    assert not both.stop and both.has_fixes and both.needs_person
    low = Issue(part="subline", problem="weak", severity="high", fix="regenerate_copy")
    p = plan_fixes(crit(low), 0, 3, 0.5, 1.0)
    assert p.stop and "budget" in p.reason


# --- a whole session against a scripted model ------------------------------------------

def scripted_client():
    intent = Intent(medium="poster", purpose="10th birthday", audience="family", feeling="wonder, then warmth",
                    personal_detail="she named a star after the cat", avoid=["pink"])
    concept = Concept(title="Ten Orbits", idea="the cat-star at the centre of ten orbits", why_personal="the star",
                      mood="quiet wonder", palette=["#102030", "#f5efe6", "#f0a030", "#8899aa"],
                      typography="Georgia headline", composition="star centred, title below")
    briefs = Briefs.model_validate({
        "copy_brief": {"slots": ["headline", "subline"], "voice": "warm", "content": "Mira turns ten",
                       "limits": "headline <= 3 words"},
        "illustration": {"subject": "a star with whiskers", "style": "flat", "palette": concept.palette,
                         "motif": "cat-star"},
        "layout": {"composition": "centred", "typography": "Georgia", "slots": ["headline", "subline", "illustration"],
                   "palette": {"bg": "#102030", "fg": "#f5efe6", "accent": "#f0a030", "muted": "#8899aa"},
                   "mood": "quiet"}})
    fix = Issue(part="headline", problem="slightly heavy", severity="medium", fix="edit",
                edits=[EditOp(tool="style", args={"slot": "headline", "css": "font-size: 64px"})])
    by_schema = {
        IntentDraft: [IntentDraft(intent=intent, summary="A warm star poster for Mira's 10th.")],
        Concepts: [Concepts(concepts=[concept])],
        Briefs: [briefs],
        Copy: [Copy(texts=[{"slot": "headline", "text": "Ten Orbits"}, {"slot": "subline", "text": "Mira, 10"}])],
        Critique: [crit(fix), crit(serves=True)],
    }
    text_by_purpose = {"agent:illustration": f"Here it is:\n{SVG}", "agent:layout": LAYOUT}
    requests = []

    def usage():
        return SimpleNamespace(input_tokens=2000, output_tokens=800,
                               cache_creation_input_tokens=0, cache_read_input_tokens=0)

    class Messages:
        def parse(self, **kw):
            requests.append(kw)
            out = by_schema[kw["output_format"]].pop(0)
            return SimpleNamespace(stop_reason="end_turn", stop_details=None, model=kw["model"],
                                   usage=usage(), parsed_output=out, content=[])

        def create(self, **kw):
            requests.append(kw)
            text = LAYOUT if "1080x1350" in kw["system"][0]["text"] else f"Here it is:\n{SVG}"
            return SimpleNamespace(stop_reason="end_turn", stop_details=None, model=kw["model"], usage=usage(),
                                   content=[SimpleNamespace(type="text", text=text)])

        def stream(self, **kw):
            kw["streamed"] = True
            msg = self.create(**kw)

            class Ctx:
                def __enter__(self):
                    return SimpleNamespace(get_final_message=lambda: msg)

                def __exit__(self, *exc):
                    return False
            return Ctx()

    return SimpleNamespace(beta=SimpleNamespace(messages=Messages())), requests


def test_session_needs_consent_before_sending_answers(tmp_path):
    client, requests = scripted_client()
    s = Session(tmp_path, budget=5, client=client)
    with pytest.raises(NeedsApproval):
        s.draft_intent("poster", [InterviewTurn(question="q", answer="a")])
    assert requests == []


def test_session_end_to_end(tmp_path):
    client, requests = scripted_client()
    s = Session(tmp_path, budget=5, client=client)
    s.consent_to_send()
    draft = s.draft_intent("poster", [InterviewTurn(question="What for?", answer="Mira's 10th birthday")])
    s.confirm_intent(draft)
    concept = s.concepts()[0]
    s.choose(concept)
    with Renderer() as r:
        first = s.produce(r)
        final, c, plan = s.refine(r, first, max_rounds=3)
    assert plan.stop and "serves the intent" in plan.reason
    layout = next(p for p in s.timeline.state.parts if p.role == "layout")
    assert len(s.renders) == 2 and layout.edits[0].tool == "style"
    # specialists ran on Sonnet, the director on Opus; agents never saw the full working state
    models = {r_["model"] for r_ in requests}
    assert models == {"claude-opus-5-5", "claude-sonnet-5-5"}
    for r_ in requests:
        if r_["model"] == "claude-sonnet-5-5":
            assert len(r_["system"]) == 1  # no pinned working state for agents
            if "output_format" not in r_:
                assert r_.get("streamed")  # long SVG/HTML outputs stream
    # export is irreversible: refused without approval, allowed with it
    with pytest.raises(PermissionError):
        s.export(tmp_path / "out", approved=False)
    out = s.export(tmp_path / "out", approved=True)
    prov = json.loads(out.with_suffix(".provenance.json").read_text())
    assert {p["role"] for p in prov["parts"]} == {"copy", "illustration", "layout"}
    assert s.llm.spent > 0 and (s.dir / "episodes.jsonl").exists()
    assert any(e["action"] == Action.EXPORT.value and e["allowed"] for e in s.gate.log)


def test_empty_copy_is_an_error(tmp_path):
    from media_director.agents import AgentOutputError, CopyBrief, write_copy
    from media_director.gates import Gate, Grant
    from media_director.llm import LLM

    class M:
        def parse(self, **kw):
            u = SimpleNamespace(input_tokens=1, output_tokens=1, cache_creation_input_tokens=0, cache_read_input_tokens=0)
            return SimpleNamespace(stop_reason="end_turn", stop_details=None, model=kw["model"], usage=u,
                                   parsed_output=Copy(texts=[]), content=[])
    gate = Gate([Grant(Action.SPEND, limit=1), Grant(Action.SEND_PERSONAL, scope="claude-api")])
    gate.approve(Action.SEND_PERSONAL, "claude-api", once=False)
    llm = LLM(gate=gate, client=SimpleNamespace(beta=SimpleNamespace(messages=M())))
    with pytest.raises(AgentOutputError):
        write_copy(llm, AssetStore(tmp_path), CopyBrief(slots=["headline"], voice="v", content="c", limits="l"))
