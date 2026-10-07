import json

import pytest

from media_director.claude_cli import ClaudeCLIError, ClaudeCodeClient, make_client
from media_director.director import IntentDraft
from media_director.gates import Action, Gate, Grant
from media_director.llm import LLM, image_block
from test_manual import PNG


def result_line(**kw):
    base = {"type": "result", "subtype": "success", "is_error": False, "result": "ok", "total_cost_usd": 0.0123,
            "usage": {"input_tokens": 10, "output_tokens": 20, "cache_creation_input_tokens": 0,
                      "cache_read_input_tokens": 0}}
    base.update(kw)
    return json.dumps(base)


class Runner:
    def __init__(self, *outputs):
        self.outputs, self.calls = list(outputs), []

    def __call__(self, argv, stdin, timeout):
        self.calls.append((argv, json.loads(stdin)))
        return "\n".join(['{"type":"system","subtype":"init"}', self.outputs.pop(0)])


def llm_with(runner):
    gate = Gate([Grant(Action.SPEND, limit=5), Grant(Action.SEND_PERSONAL, scope="claude-api")])
    gate.approve(Action.SEND_PERSONAL, "claude-api", once=False)
    return LLM(gate=gate, client=ClaudeCodeClient(binary="/usr/bin/claude", runner=runner))


def test_structured_call_goes_through_claude_p():
    draft = {"intent": {"medium": "poster", "purpose": "birthday", "audience": "family", "feeling": "warm",
                        "personal_detail": "the cat-star", "must_include": [], "avoid": [], "open_questions": []},
             "summary": "A warm poster."}
    runner = Runner(result_line(result=json.dumps(draft), structured_output=draft))
    llm = llm_with(runner)
    out = llm.structured(model="claude-opus-5-5", system="sys", content="hi", schema=IntentDraft, purpose="t",
                         pinned="<working_state/>")
    assert out.intent.personal_detail == "the cat-star"
    argv, msg = runner.calls[0]
    for flag in ("-p", "--no-session-persistence", "--json-schema"):
        assert flag in argv
    assert argv[argv.index("--model") + 1] == "claude-opus-5-5"
    assert argv[argv.index("--tools") + 1] == "" and argv[argv.index("--setting-sources") + 1] == ""
    assert "<working_state/>" in argv[argv.index("--system-prompt") + 1]  # pinned W reaches the CLI
    assert msg["message"]["content"] == [{"type": "text", "text": "hi"}]
    assert llm.spent == pytest.approx(0.0123)  # the CLI's reported cost is used


def test_images_and_long_outputs():
    runner = Runner(result_line(result="<svg/>"), result_line(result="looks fine"))
    llm = llm_with(runner)
    assert llm.text(model="claude-sonnet-5-5", system="s", content="draw", purpose="t", max_tokens=32000) == "<svg/>"
    llm.text(model="claude-opus-5-5", system="s", content=[image_block(PNG), {"type": "text", "text": "?"}],
             purpose="t", effort="high")
    argv, msg = runner.calls[1]
    assert msg["message"]["content"][0]["type"] == "image"
    assert argv[argv.index("--effort") + 1] == "high"


def test_errors_are_raised():
    llm = llm_with(Runner(result_line(is_error=True, subtype="error_during_execution", result="boom")))
    with pytest.raises(ClaudeCLIError):
        llm.text(model="claude-opus-5-5", system="s", content="x", purpose="t")
    with pytest.raises(ValueError):
        make_client("nope")


def test_make_client_and_default_backend():
    from media_director.claude_cli import DEFAULT_BACKEND
    from media_director.cli import main  # noqa: F401  (imports cleanly)
    assert DEFAULT_BACKEND == "claude-code"
    assert make_client("api") is None
