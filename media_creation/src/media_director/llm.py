"""Claude client wrapper: models, structured output, images, cost tracking.

The director runs on Claude Opus 5.5 and specialist agents on Claude Sonnet
5.5. Every call checks the action gate for spending first and charges the
actual cost afterwards. Server-side refusal fallbacks are on ("default").
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, TypeVar

import anthropic
from pydantic import BaseModel

from .gates import Action, Gate
from .sources import Source

DIRECTOR_MODEL = "claude-opus-5-5"
SPECIALIST_MODEL = "claude-sonnet-5-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
PERSONAL_SCOPE = "claude-api"

# Dollars per million tokens: input, output, cache read. Cache writes bill at
# 1.25x input.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20),
}

# A conservative per-call estimate used to check the budget before a call.
ESTIMATE = {"claude-opus-5-5": 0.40, "claude-sonnet-5-5": 0.20}

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


class Refused(LLMError):
    pass


class Truncated(LLMError):
    pass


class BudgetExceeded(LLMError):
    pass


class NeedsApproval(LLMError):
    """Personal material would leave the machine without the person's approval."""


def cost_of(model: str, usage: Any) -> float:
    price_in, price_out, price_cache = PRICES.get(model, PRICES[DIRECTOR_MODEL])
    get = lambda name: getattr(usage, name, 0) or 0  # noqa: E731
    return (
        get("input_tokens") * price_in
        + get("cache_creation_input_tokens") * price_in * 1.25
        + get("cache_read_input_tokens") * price_cache
        + get("output_tokens") * price_out
    ) / 1_000_000


def image_block(png: bytes) -> dict:
    return {"type": "image",
            "source": {"type": "base64", "media_type": "image/png",
                       "data": base64.standard_b64encode(png).decode("ascii")}}


@dataclass
class LLM:
    gate: Gate
    client: Any = None
    calls: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if self.client is None:
            # Resolves credentials from the environment (ANTHROPIC_API_KEY, an
            # auth token, or an `ant auth login` profile). Never hardcoded.
            self.client = anthropic.Anthropic()

    @property
    def spent(self) -> float:
        return sum(c["cost"] for c in self.calls)

    def _check_budget(self, model: str, purpose: str, personal: bool):
        if personal:
            # Sending the person's material to the model is a data flow (R9).
            p = self.gate.decide(Action.SEND_PERSONAL, Source.DIRECTOR, scope=PERSONAL_SCOPE)
            if not p.allowed:
                raise NeedsApproval(p.reason)
        d = self.gate.decide(Action.SPEND, Source.DIRECTOR, scope=model, amount=ESTIMATE[model])
        if not d.allowed:
            raise BudgetExceeded(d.reason)
        return d

    def _finish(self, decision, model: str, purpose: str, resp) -> None:
        if resp.stop_reason == "refusal":
            raise Refused(f"{purpose}: model declined ({getattr(resp.stop_details, 'category', None)})")
        if resp.stop_reason == "max_tokens":
            raise Truncated(f"{purpose}: output hit max_tokens")
        served = getattr(resp, "model", model) or model
        cost = cost_of(served, resp.usage)
        self.gate.charge(decision, cost)
        self.calls.append({"purpose": purpose, "model": served, "cost": cost,
                           "input_tokens": getattr(resp.usage, "input_tokens", 0),
                           "output_tokens": getattr(resp.usage, "output_tokens", 0),
                           "cache_read": getattr(resp.usage, "cache_read_input_tokens", 0) or 0})

    @staticmethod
    def _system(system: str, pinned: str | None) -> list[dict]:
        # Stable instructions first and cached; the pinned working state follows
        # uncached because it changes as the piece develops.
        blocks = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        if pinned:
            blocks.append({"type": "text", "text": pinned})
        return blocks

    def structured(self, *, model: str, system: str, content: list[dict] | str,
                   schema: type[T], purpose: str, pinned: str | None = None,
                   max_tokens: int = 16000, personal: bool = True) -> T:
        decision = self._check_budget(model, purpose, personal)
        resp = self.client.beta.messages.parse(
            model=model, max_tokens=max_tokens,
            system=self._system(system, pinned),
            messages=[{"role": "user", "content": content}],
            output_format=schema,
            betas=[FALLBACK_BETA], fallbacks="default",
        )
        self._finish(decision, model, purpose, resp)
        if resp.parsed_output is None:
            raise LLMError(f"{purpose}: no structured output")
        return resp.parsed_output

    def text(self, *, model: str, system: str, content: list[dict] | str,
             purpose: str, pinned: str | None = None, max_tokens: int = 16000,
             effort: str | None = None, personal: bool = True) -> str:
        decision = self._check_budget(model, purpose, personal)
        kwargs: dict[str, Any] = {}
        if effort:
            kwargs["output_config"] = {"effort": effort}
        resp = self.client.beta.messages.create(
            model=model, max_tokens=max_tokens,
            system=self._system(system, pinned),
            messages=[{"role": "user", "content": content}],
            betas=[FALLBACK_BETA], fallbacks="default", **kwargs,
        )
        self._finish(decision, model, purpose, resp)
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
