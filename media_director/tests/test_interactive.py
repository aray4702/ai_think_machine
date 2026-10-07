from media_director.interactive import Terminal, run
from test_manual import JPEG
from test_manual import scripted as scripted_manual
from test_production import scripted_client


def term(answers, out):
    feed = iter(answers)
    return Terminal(ask=lambda prompt: (out.append(prompt), next(feed))[1], say=out.append, opener=lambda p: None)


def test_declining_consent_sends_nothing(tmp_path):
    client, requests = scripted_client()
    out = []
    s = run(tmp_path, term=term(["n"], out), client=client)
    assert s is None and requests == [] and "Nothing was sent." in " ".join(map(str, out))


def test_interactive_automatic_flow(tmp_path):
    client, _ = scripted_client()
    out = []
    answers = ["y", "3",            # consent, budget
               "1", "1",            # poster, automatic
               "Mira's 10th", "wonder", "the cat-star", "no pink",  # interview
               "avoid", "pink, glitter", "",  # edit a field, then continue
               "1", "warmer amber",  # concept, note
               "2",                  # rounds
               "u", "r", "e", str(tmp_path / "out"), "y", "q"]  # undo, redo, export, quit
    s = run(tmp_path, term=term(answers, out), client=client)
    assert s.w.intent.avoid == ["pink", "glitter"]
    assert any("warmer amber" in c for c in s.w.constraints)
    assert len(s.renders) >= 3 and (tmp_path / "out" / f"{s.id}.png").exists()


def test_interactive_manual_flow(tmp_path):
    client, requests = scripted_manual()
    img = tmp_path / "result.jpg"
    img.write_bytes(JPEG)
    out = []
    answers = ["y", "2", "1", "2",   # consent, budget, poster, manual
               "Mira's 10th", "", "the cat-star", "",  # interview (two skipped)
               "",                   # no field edits
               "1", "",              # concept, no note
               "1",                  # target: first poster tool (Midjourney)
               "r", str(img), "too bright", "q"]
    s = run(tmp_path, term=term(answers, out), client=client)
    text = "\n".join(map(str, out))
    assert "--ar 4:5" in text and "darker sky" in text
    assert {r["model"] for r in requests} == {"claude-opus-5-5"}
    assert s.last_prompt().prompt.endswith("darker sky")
