"""Assembly and editing tools: cheap, deterministic, precise.

A poster is assembled from three assets: a layout (HTML with empty slots
marked data-slot="..." and its look set through CSS variables), copy (JSON
mapping slot names to text) and an illustration (SVG). Edit operations never
rewrite the generated assets; they are applied at assembly time, so every
edit can be undone by removing the operation from the timeline.
"""

from __future__ import annotations

import html
import json
import re

from .timeline import AssetStore, EditOp, PieceState

TEXT_TOOLS = {"set_text"}
STYLE_TOOLS = {"set_var", "style", "hide"}
EDIT_TOOLS = TEXT_TOOLS | STYLE_TOOLS

_SAFE_NAME = re.compile(r"^[a-zA-Z][\w-]*$")
_SAFE_CSS = re.compile(r"^[^{}<>@\\]*$")  # declarations only: no blocks, tags or at-rules


class EditError(ValueError):
    pass


def validate(op: EditOp) -> EditOp:
    """Reject edit operations that could inject markup or script."""
    a = op.args
    if op.tool not in EDIT_TOOLS:
        raise EditError(f"unknown tool {op.tool}")
    if op.tool == "set_var":
        if not _SAFE_NAME.match(a.get("name", "")) or not _SAFE_CSS.match(str(a.get("value", ""))):
            raise EditError("bad set_var")
    elif op.tool in ("style", "hide"):
        if not _SAFE_NAME.match(a.get("slot", "")):
            raise EditError("bad slot")
        if op.tool == "style" and not _SAFE_CSS.match(str(a.get("css", ""))):
            raise EditError("bad css")
    elif op.tool == "set_text":
        if not _SAFE_NAME.match(a.get("slot", "")) or not isinstance(a.get("text"), str):
            raise EditError("bad set_text")
    return op


# --- sanitizing generated HTML/SVG ----------------------------------------------

_SCRIPT = re.compile(r"<script\b.*?</script\s*>", re.I | re.S)
_EVENT_ATTR = re.compile(r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
_JS_URL = re.compile(r"(href|src|xlink:href)\s*=\s*([\"'])\s*javascript:[^\"']*\2", re.I)
_EXTERNAL_LINK = re.compile(r"<link\b(?![^>]*fonts\.googleapis\.com)[^>]*>", re.I)
_IFRAME = re.compile(r"<(iframe|object|embed)\b.*?(</\1\s*>|/?>)", re.I | re.S)


def sanitize(markup: str) -> str:
    """Strip scripts, event handlers, javascript: URLs, frames and non-font links."""
    for pattern, repl in ((_SCRIPT, ""), (_IFRAME, ""), (_EVENT_ATTR, ""),
                          (_JS_URL, r'\1=\2#\2'), (_EXTERNAL_LINK, "")):
        markup = pattern.sub(repl, markup)
    return markup


def extract(markup: str, tag: str) -> str:
    """Pull the first complete <tag>...</tag> out of a model reply."""
    m = re.search(rf"<{tag}\b.*?</{tag}\s*>", markup, re.S | re.I)
    if not m:
        raise EditError(f"no <{tag}> found")
    return m.group(0)


# --- assembly --------------------------------------------------------------------

def fill_slot(page: str, slot: str, inner: str) -> str:
    pattern = re.compile(rf'(<(\w+)\b[^>]*\bdata-slot="{re.escape(slot)}"[^>]*>)(.*?)(</\2\s*>)', re.S)
    if not pattern.search(page):
        return page
    return pattern.sub(lambda m: m.group(1) + inner + m.group(4), page, count=1)


def slots_in(page: str) -> list[str]:
    return re.findall(r'data-slot="([\w-]+)"', page)


def assemble(state: PieceState, store: AssetStore) -> str:
    """Build the final HTML for a single-page piece from its parts and edits."""
    parts = {p.role: p for p in state.parts}
    if "layout" not in parts:
        raise EditError("piece has no layout")
    page = store.get(parts["layout"].asset_id).decode()

    copy: dict[str, str] = {}
    if "copy" in parts:
        copy = json.loads(store.get(parts["copy"].asset_id))
        for op in parts["copy"].edits:
            if op.tool == "set_text":
                copy[op.args["slot"]] = op.args["text"]
    for slot, text in copy.items():
        lines = "<br>".join(html.escape(line) for line in str(text).split("\n"))
        page = fill_slot(page, slot, lines)

    if "illustration" in parts:
        svg = store.get(parts["illustration"].asset_id).decode()
        page = fill_slot(page, "illustration", svg)

    rules: list[str] = []
    for p in state.parts:
        for op in p.edits:
            a = op.args
            if op.tool == "set_var":
                rules.append(f":root {{ --{a['name']}: {a['value']}; }}")
            elif op.tool == "style":
                rules.append(f'[data-slot="{a["slot"]}"] {{ {a["css"]} }}')
            elif op.tool == "hide":
                rules.append(f'[data-slot="{a["slot"]}"] {{ display: none !important; }}')
    if rules:
        style = '<style id="edits">\n' + "\n".join(rules) + "\n</style>"
        page = page.replace("</head>", style + "\n</head>", 1) if "</head>" in page else style + page
    return sanitize(page)
