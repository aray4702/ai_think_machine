"""The timeline: a non-destructive, versioned scratch (R2).

Generated assets are stored once and never changed, keyed by the hash of
their content. A piece is a list of parts; each part points at an asset and
carries a list of edit operations applied at render time. Every change to a
piece is a new version, so any edit can be undone exactly and a piece can be
forked to try an alternative. Only export leaves the timeline.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field


class AssetStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes, suffix: str, meta: dict | None = None) -> str:
        asset_id = hashlib.sha256(data).hexdigest()[:16] + suffix
        path = self.root / asset_id
        if not path.exists():  # immutable: identical content maps to one file
            path.write_bytes(data)
            (self.root / f"{asset_id}.meta.json").write_text(json.dumps(meta or {}, indent=2))
        return asset_id

    def get(self, asset_id: str) -> bytes:
        return (self.root / asset_id).read_bytes()

    def meta(self, asset_id: str) -> dict:
        p = self.root / f"{asset_id}.meta.json"
        return json.loads(p.read_text()) if p.exists() else {}


class EditOp(BaseModel):
    """One edit. Fixed fields rather than a free-form dict, so that strict
    structured outputs can carry it; unused fields stay empty."""

    tool: str = Field(description="set_var, style, hide or set_text")
    slot: str = Field(default="", description="For style, hide, set_text: the data-slot name")
    name: str = Field(default="", description="For set_var: the CSS variable name without --")
    value: str = Field(default="", description="For set_var: the new value")
    css: str = Field(default="", description="For style: CSS declarations, e.g. 'font-size: 64px'")
    text: str = Field(default="", description="For set_text: the new text")


class Part(BaseModel):
    id: str
    role: str  # e.g. "poster", "slide-1", "illustration"
    asset_id: str
    edits: list[EditOp] = Field(default_factory=list)


class PieceState(BaseModel):
    parts: list[Part] = Field(default_factory=list)
    note: str = ""


class Timeline:
    """Versions of one piece. History is append-only; undo moves a cursor."""

    def __init__(self, name: str, parent: str | None = None):
        self.name = name
        self.parent = parent
        self.versions: list[PieceState] = [PieceState(note="empty")]
        self.cursor = 0

    @property
    def state(self) -> PieceState:
        return self.versions[self.cursor]

    def _commit(self, new: PieceState) -> PieceState:
        # Committing after an undo drops the undone future, as editors do;
        # the dropped versions stay recoverable through forks taken earlier.
        self.versions = self.versions[: self.cursor + 1] + [new]
        self.cursor = len(self.versions) - 1
        return new

    def set_part(self, part: Part, note: str) -> PieceState:
        parts = [p for p in self.state.parts if p.id != part.id]
        order = [p.id for p in self.state.parts]
        parts.append(part)
        parts.sort(key=lambda p: order.index(p.id) if p.id in order else len(order))
        return self._commit(PieceState(parts=parts, note=note))

    def edit(self, part_id: str, op: EditOp, note: str = "") -> PieceState:
        parts = []
        for p in self.state.parts:
            if p.id == part_id:
                p = p.model_copy(update={"edits": p.edits + [op]})
            parts.append(p)
        if not any(p.id == part_id for p in parts):
            raise KeyError(part_id)
        return self._commit(PieceState(parts=parts, note=note or f"{op.tool} on {part_id}"))

    def reorder(self, order: list[str], note: str = "reorder") -> PieceState:
        by_id = {p.id: p for p in self.state.parts}
        if sorted(order) != sorted(by_id):
            raise ValueError("reorder must list every part exactly once")
        return self._commit(PieceState(parts=[by_id[i] for i in order], note=note))

    def undo(self) -> PieceState:
        self.cursor = max(0, self.cursor - 1)
        return self.state

    def redo(self) -> PieceState:
        self.cursor = min(len(self.versions) - 1, self.cursor + 1)
        return self.state

    def fork(self, name: str) -> "Timeline":
        t = Timeline(name, parent=self.name)
        t.versions = [self.state.model_copy(deep=True)]
        return t

    def to_json(self) -> str:
        return json.dumps({
            "name": self.name, "parent": self.parent, "cursor": self.cursor,
            "versions": [v.model_dump() for v in self.versions],
        }, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Timeline":
        d = json.loads(text)
        t = cls(d["name"], d.get("parent"))
        t.versions = [PieceState.model_validate(v) for v in d["versions"]]
        t.cursor = d["cursor"]
        return t
