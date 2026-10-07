"""Claude Code CLI backend: run the director and agents through `claude -p`.

This uses the person's Claude Code login (for example a Claude subscription)
instead of per-token API billing. The adapter offers the same small surface
as the SDK client that LLM uses - beta.messages.parse / create / stream - so
nothing else changes. Requests run with every tool disabled, no saved
session, no settings files, and from an empty working directory so that no
project instructions leak in.

The CLI reports `total_cost_usd`; on a subscription that is the notional API
cost, and the budget grant still caps it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
from typing import Any, Callable

from pydantic import BaseModel

Runner = Callable[[list[str], str, int], str]  # (argv, stdin, timeout) -> stdout


class ClaudeCLIError(RuntimeError):
    pass


def _default_runner(argv: list[str], stdin: str, timeout: int) -> str:
    with tempfile.TemporaryDirectory(prefix="media-director-") as cwd:
        proc = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    if proc.returncode != 0 and not proc.stdout.strip():
        raise ClaudeCLIError(f"claude exited with {proc.returncode}: {proc.stderr.strip()[:500]}")
    return proc.stdout


def _system_text(system: Any) -> str:
    if isinstance(system, str):
        return system
    return "\n\n".join(b["text"] for b in system or [] if b.get("type") == "text")


def _content_blocks(content: Any) -> list[dict]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return [{k: v for k, v in b.items() if k != "cache_control"} for b in content]


class _Messages:
    def __init__(self, binary: str, runner: Runner, timeout: int):
        self.binary, self.runner, self.timeout = binary, runner, timeout

    def _run(self, *, model: str, system: Any, messages: list[dict],
             schema: type[BaseModel] | None = None, output_config: dict | None = None, **_ignored) -> SimpleNamespace:
        # betas, fallbacks, cache_control and max_tokens are API-only and ignored here.
        argv = [self.binary, "-p", "--input-format", "stream-json", "--output-format", "stream-json",
                "--verbose", "--model", model, "--system-prompt", _system_text(system),
                "--tools", "", "--no-session-persistence", "--setting-sources", ""]
        if schema is not None:
            argv += ["--json-schema", json.dumps(schema.model_json_schema())]
        if output_config and output_config.get("effort"):
            argv += ["--effort", output_config["effort"]]
        user = {"type": "user", "message": {"role": "user", "content": _content_blocks(messages[0]["content"])}}
        out = self.runner(argv, json.dumps(user) + "\n", self.timeout)

        result = None
        for line in out.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            event = json.loads(line)
            if event.get("type") == "result":
                result = event
        if result is None:
            raise ClaudeCLIError("no result from claude -p")
        if result.get("is_error") or result.get("subtype") != "success":
            raise ClaudeCLIError(f"claude -p failed: {result.get('subtype')}: {str(result.get('result'))[:300]}")

        u = result.get("usage") or {}
        usage = SimpleNamespace(input_tokens=u.get("input_tokens", 0), output_tokens=u.get("output_tokens", 0),
                                cache_creation_input_tokens=u.get("cache_creation_input_tokens", 0),
                                cache_read_input_tokens=u.get("cache_read_input_tokens", 0))
        parsed = None
        if schema is not None:
            data = result.get("structured_output")
            if data is None:
                data = json.loads(result.get("result") or "null")
            parsed = schema.model_validate(data)
        return SimpleNamespace(stop_reason="end_turn", stop_details=None, model=model, usage=usage,
                               parsed_output=parsed, cost_usd=result.get("total_cost_usd"),
                               content=[SimpleNamespace(type="text", text=result.get("result") or "")])

    def parse(self, *, output_format: type[BaseModel], **kw) -> SimpleNamespace:
        return self._run(schema=output_format, **kw)

    def create(self, **kw) -> SimpleNamespace:
        return self._run(**kw)

    def stream(self, **kw):
        # The CLI streams internally; hand back the finished message.
        resp = self._run(**kw)

        class _Ctx:
            def __enter__(self):
                return SimpleNamespace(get_final_message=lambda: resp)

            def __exit__(self, *exc):
                return False
        return _Ctx()


class ClaudeCodeClient:
    """Drop-in for the parts of anthropic.Anthropic() that LLM uses."""

    def __init__(self, binary: str | None = None, runner: Runner | None = None, timeout: int = 900):
        found = binary or shutil.which("claude")
        if not found:
            raise ClaudeCLIError("the `claude` command was not found; install Claude Code or use --backend api")
        self.beta = SimpleNamespace(messages=_Messages(found, runner or _default_runner, timeout))


BACKENDS = ("claude-code", "api")
DEFAULT_BACKEND = "claude-code"  # the person's Claude Code login; "api" uses per-token API billing


def make_client(backend: str):
    """None means: let LLM create the default Anthropic API client."""
    if backend == "api":
        return None
    if backend == "claude-code":
        return ClaudeCodeClient()
    raise ValueError(f"unknown backend {backend}; choose one of {', '.join(BACKENDS)}")
