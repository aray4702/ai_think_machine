"""Specialist agents: expensive, stochastic, creative.

Each agent receives only a narrowed brief from the director - never the
person's whole history - and returns raw material. Its output is data: it is
sanitized, stored unchanged in the asset store with its provenance, and can
neither change the goal nor request actions.
"""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field

from .llm import LLM, SPECIALIST_MODEL
from .sources import Source, Tagged
from .timeline import AssetStore
from .tools import extract, sanitize

CSS_VARS = ["bg", "fg", "accent", "muted", "font-head", "font-body"]


class CopyBrief(BaseModel):
    slots: list[str] = Field(description="Slot names to write, e.g. headline, subline, body, footer")
    voice: str = Field(description="Tone and voice, in the person's terms")
    content: str = Field(description="What the text must say, including required names and dates")
    limits: str = Field(description="Length limits per slot")


class IllustrationBrief(BaseModel):
    subject: str
    style: str
    palette: list[str] = Field(description="Hex colors to use")
    motif: str = Field(description="The personal detail or metaphor to embody")
    avoid: list[str] = Field(default_factory=list)


class LayoutBrief(BaseModel):
    composition: str = Field(description="Arrangement, hierarchy and use of space")
    typography: str = Field(description="Typefaces and treatment; Google Fonts or system stacks only")
    palette: dict[str, str] = Field(description="Values for the CSS variables bg, fg, accent, muted")
    slots: list[str] = Field(description="Text slots plus 'illustration'")
    mood: str


class Copy(BaseModel):
    texts: dict[str, str] = Field(description="Slot name to text")


COPY_SYSTEM = """\
You write the words for one personal poster. Write in the voice described,
concretely and briefly, and never generically. Respect the length limits.
Return text for exactly the slots requested."""

ILLUSTRATION_SYSTEM = """\
You draw one illustration as a single self-contained SVG for a personal poster.
Rules: one <svg> element with a viewBox and no fixed width/height; no <script>,
no external references, no embedded raster images, no text unless asked. Use
only the given palette. Prefer a distinctive, specific image over a generic
one. Reply with the SVG only."""

LAYOUT_SYSTEM = f"""\
You lay out one personal poster as a complete HTML document for a canvas of
exactly 1080x1350 CSS pixels.
Rules:
- Define these CSS variables on :root and use them for all colors and fonts:
  {", ".join("--" + v for v in CSS_VARS)}.
- For each slot, include one element with data-slot="<name>" and leave it EMPTY.
  The illustration slot is a block element that will receive an inline SVG
  (style its svg child to fit, e.g. width:100%;height:100%).
- Every slot must stay inside the canvas, and text boxes must be large enough
  for their text: size type with clamp() or fixed px suited to the limits.
- Text must have strong contrast with its background.
- Fonts: system stacks or Google Fonts via <link>. No scripts, no other
  external resources.
Reply with the HTML document only."""


def _store(store: AssetStore, data: str, suffix: str, agent: str, brief: BaseModel) -> str:
    brief_json = brief.model_dump_json()
    meta = {"agent": agent, "model": SPECIALIST_MODEL, "source": Source.AGENT.value,
            "brief_sha": hashlib.sha256(brief_json.encode()).hexdigest()[:12], "brief": json.loads(brief_json)}
    return store.put(data.encode(), suffix, meta)


def write_copy(llm: LLM, store: AssetStore, brief: CopyBrief) -> tuple[str, Tagged]:
    copy = llm.structured(model=SPECIALIST_MODEL, system=COPY_SYSTEM, schema=Copy,
                          content=brief.model_dump_json(indent=2), purpose="agent:copy")
    texts = {k: v for k, v in copy.texts.items() if k in brief.slots}
    data = json.dumps(texts, indent=2, ensure_ascii=False)
    return _store(store, data, ".json", "copy", brief), Tagged(Source.AGENT, "copy", data)


def draw_illustration(llm: LLM, store: AssetStore, brief: IllustrationBrief) -> tuple[str, Tagged]:
    reply = llm.text(model=SPECIALIST_MODEL, system=ILLUSTRATION_SYSTEM,
                     content=brief.model_dump_json(indent=2), purpose="agent:illustration",
                     max_tokens=32000)
    svg = sanitize(extract(reply, "svg"))
    return _store(store, svg, ".svg", "illustration", brief), Tagged(Source.AGENT, "illustration", svg)


def lay_out(llm: LLM, store: AssetStore, brief: LayoutBrief) -> tuple[str, Tagged]:
    reply = llm.text(model=SPECIALIST_MODEL, system=LAYOUT_SYSTEM,
                     content=brief.model_dump_json(indent=2), purpose="agent:layout",
                     max_tokens=32000)
    page = sanitize(extract(reply, "html"))
    return _store(store, page, ".html", "layout", brief), Tagged(Source.AGENT, "layout", page)
