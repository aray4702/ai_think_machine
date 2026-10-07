from types import SimpleNamespace

import pytest

from media_director.director import Concept, Concepts, IntentDraft, InterviewTurn
from media_director.llm import media_type
from media_director.prompts import TARGETS, FinalPrompt, Revision, to_markdown
from media_director.session import Session
from media_director.working import Intent

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
JPEG = b"\xff\xd8\xff\xe0" + b"0" * 32


def scripted():
    intent = Intent(medium="poster", purpose="10th birthday", audience="family", feeling="wonder",
                    personal_detail="she named a star after the cat", must_include=["Mira", "10"], avoid=["pink"])
    concept = Concept(title="Ten Orbits", idea="cat-star", why_personal="the star", mood="quiet",
                      palette=["#102030", "#f5efe6", "#f0a030", "#8899aa"], typography="serif",
                      composition="centred")
    first = FinalPrompt(target="midjourney", prompt="a small star with whiskers over a night balcony",
                        parameters="--ar 4:5 --no pink, cartoon", text_to_add_afterwards=["Mira, 10"],
                        variations=["a", "b"], tips=["add the date in an editor"])
    revised = first.model_copy(update={"prompt": "a small amber star with whiskers, darker sky"})
    queue = {IntentDraft: [IntentDraft(intent=intent, summary="star poster")],
             Concepts: [Concepts(concepts=[concept])],
             FinalPrompt: [first],
             Revision: [Revision(what_works=["the star"], what_misses_the_intent=["too bright"], revised=revised)]}
    requests = []

    class Messages:
        def parse(self, **kw):
            requests.append(kw)
            usage = SimpleNamespace(input_tokens=1500, output_tokens=600,
                                    cache_creation_input_tokens=0, cache_read_input_tokens=0)
            return SimpleNamespace(stop_reason="end_turn", stop_details=None, model=kw["model"], usage=usage,
                                   parsed_output=queue[kw["output_format"]].pop(0), content=[])

    return SimpleNamespace(beta=SimpleNamespace(messages=Messages())), requests


def test_media_type_detection():
    assert media_type(PNG) == "image/png" and media_type(JPEG) == "image/jpeg"
    with pytest.raises(ValueError):
        media_type(b"not an image")


def test_every_target_has_conventions():
    assert {"midjourney", "chatgpt-image", "ideogram", "stable-diffusion", "flux", "gamma", "generic"} <= set(TARGETS)
    assert all(t.conventions and t.media for t in TARGETS.values())


def test_manual_prompt_and_revise_round_trip(tmp_path):
    client, requests = scripted()
    s = Session(tmp_path, budget=3, client=client)
    s.consent_to_send()
    s.confirm_intent(s.draft_intent("poster", [InterviewTurn(question="q", answer="Mira's 10th")]))
    s.choose(s.concepts()[0])
    fp, md = s.manual_prompt("midjourney")
    text = md.read_text()
    assert "whiskers" in text and "--ar 4:5" in text and "personal details" in text
    # manual mode uses only the director; no specialist agents, no rendering
    assert {r["model"] for r in requests} == {"claude-opus-5-5"}
    ask = requests[-1]["messages"][0]["content"]
    assert "Midjourney" in ask and "--ar 4:5" in ask  # tool conventions reach the director

    # resume the saved session and bring back a JPEG result
    s2 = Session.load(tmp_path, s.id, budget=3, client=client)
    s2.consent_to_send()
    assert s2.concept.title == "Ten Orbits" and s2.w.intent.personal_detail.startswith("she named")
    rev, md2 = s2.revise(JPEG, "too bright")
    img = requests[-1]["messages"][0]["content"][0]
    assert img["type"] == "image" and img["source"]["media_type"] == "image/jpeg"
    assert "darker sky" in md2.read_text() and (s2.dir / "result-00.jpg").exists()
    assert s2.last_prompt().prompt.endswith("darker sky")


def test_markdown_omits_empty_sections():
    md = to_markdown(FinalPrompt(target="flux", prompt="x"))
    assert "Negative prompt" not in md and "## Prompt" in md
