"""Episodic log E: an append-only record of what happened, with salience tags."""

from __future__ import annotations

import json
import time
from pathlib import Path


class EventLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, kind: str, salience: list[str] | None = None, **data) -> dict:
        event = {"t": time.time(), "kind": kind, "salience": salience or [], **data}
        with self.path.open("a") as f:
            f.write(json.dumps(event, default=str) + "\n")
        return event

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]
