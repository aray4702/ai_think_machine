"""Local web UI for the media director.

Binds to 127.0.0.1 only. Slow steps (intent, concepts, production, prompts)
run as background jobs that the page polls; each session runs one job at a
time. Rendering happens inside the job's own thread, because Playwright's
sync API must stay on the thread that started it.
"""

from __future__ import annotations

import base64
import re
import threading
import traceback
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .claude_cli import DEFAULT_BACKEND
from .director import INTERVIEW_QUESTIONS, IntentDraft, InterviewTurn
from .llm import LLMError
from .prompts import TARGETS
from .render import Renderer
from .session import Session

STATIC = Path(__file__).parent / "web"
SAFE_FILE = re.compile(r"^(render-\d+\.(png|html)|prompt-\d+-[\w-]+\.md|result-\d+\.(png|jpg|webp|gif))$")
MAX_UPLOAD = 15 * 1024 * 1024


@dataclass
class Job:
    id: str
    kind: str
    status: str = "running"  # running | done | error
    result: Any = None
    error: str = ""
    events_at_start: int = 0


@dataclass
class Entry:
    session: Session
    lock: threading.Lock = field(default_factory=threading.Lock)
    concepts: list = field(default_factory=list)
    draft: IntentDraft | None = None
    pending_question: list[str] = field(default_factory=list)
    last_critique: dict | None = None


# --- request bodies ----------------------------------------------------------------

class NewSession(BaseModel):
    budget: float = 3.0


class IntentRequest(BaseModel):
    medium: str = "poster"
    answers: list[str]


class OpenAnswer(BaseModel):
    question: str
    answer: str


class ConfirmRequest(BaseModel):
    draft: IntentDraft
    open_answers: list[OpenAnswer] = []


class ChooseRequest(BaseModel):
    index: int
    note: str = ""


class ProduceRequest(BaseModel):
    rounds: int = 2


class FeedbackRequest(BaseModel):
    text: str
    rounds: int = 2


class PromptRequest(BaseModel):
    target: str


class ReviseRequest(BaseModel):
    image_base64: str
    note: str = ""


class ExportRequest(BaseModel):
    approved: bool


def create_app(workspace: Path, client_factory: Callable[[], Any] | None = None,
               backend: str = DEFAULT_BACKEND) -> FastAPI:
    app = FastAPI(title="Media director")
    sessions: dict[str, Entry] = {}
    jobs: dict[str, Job] = {}
    workspace = Path(workspace)

    def entry(sid: str) -> Entry:
        e = sessions.get(sid)
        if e is None:
            raise HTTPException(404, "no such session")
        return e

    def start(e: Entry, kind: str, fn: Callable[[], Any]) -> dict:
        if not e.lock.acquire(blocking=False):
            raise HTTPException(409, "this session is already working on something")
        job = Job(id=uuid.uuid4().hex[:10], kind=kind, events_at_start=len(e.session.log.read()))
        jobs[job.id] = job

        def run():
            try:
                job.result = fn()
                job.status = "done"
            except LLMError as err:
                job.status, job.error = "error", str(err)
            except PermissionError as err:
                job.status, job.error = "error", str(err)
            except Exception as err:  # surface unexpected failures to the page
                job.status, job.error = "error", f"{type(err).__name__}: {err}"
                traceback.print_exc()
            finally:
                e.lock.release()

        threading.Thread(target=run, daemon=True).start()
        return {"job": job.id}

    def outcome(e: Entry, rendered, crit, plan) -> dict:
        e.last_critique = crit.model_dump()
        e.pending_question = plan.ask + plan.revise_concept
        return {"defects": [d.model_dump() for d in rendered.defects], "critique": e.last_critique,
                "stopped": plan.reason, "questions": e.pending_question, "state": e.session.summary()}

    # --- sessions and consent ---------------------------------------------------------
    @app.post("/api/sessions")
    def new_session(body: NewSession):
        if not 0 < body.budget <= 20:
            raise HTTPException(400, "budget must be between $0 and $20")
        client = client_factory() if client_factory else None
        s = Session(workspace, budget=body.budget, client=client, backend=backend)
        sessions[s.id] = Entry(session=s)
        return {"id": s.id, "questions": INTERVIEW_QUESTIONS, "targets": {k: t.label for k, t in TARGETS.items()}}

    @app.post("/api/sessions/{sid}/consent")
    def consent(sid: str):
        entry(sid).session.consent_to_send()
        return {"ok": True}

    @app.get("/api/sessions/{sid}")
    def state(sid: str):
        e = entry(sid)
        return {**e.session.summary(), "questions": e.pending_question, "critique": e.last_critique}

    # --- interview and intent ----------------------------------------------------------
    @app.post("/api/sessions/{sid}/intent")
    def intent(sid: str, body: IntentRequest):
        e = entry(sid)
        turns = [InterviewTurn(question=q, answer=a) for q, a in zip(INTERVIEW_QUESTIONS, body.answers) if a.strip()]
        if not turns:
            raise HTTPException(400, "answer at least one question")

        def run():
            e.draft = e.session.draft_intent(body.medium, turns)
            return e.draft.model_dump()
        return start(e, "intent", run)

    @app.post("/api/sessions/{sid}/intent/confirm")
    def confirm(sid: str, body: ConfirmRequest):
        e = entry(sid)
        e.session.confirm_intent(body.draft, [(a.question, a.answer) for a in body.open_answers])
        return e.session.summary()

    # --- concepts ------------------------------------------------------------------------
    @app.post("/api/sessions/{sid}/concepts")
    def concepts(sid: str):
        e = entry(sid)

        def run():
            e.concepts = e.session.concepts()
            return [c.model_dump() for c in e.concepts]
        return start(e, "concepts", run)

    @app.post("/api/sessions/{sid}/choose")
    def choose(sid: str, body: ChooseRequest):
        e = entry(sid)
        if not 0 <= body.index < len(e.concepts):
            raise HTTPException(400, "no such concept")
        e.session.choose(e.concepts[body.index], note=body.note)
        return e.session.summary()

    # --- automatic mode -------------------------------------------------------------------
    @app.post("/api/sessions/{sid}/produce")
    def produce(sid: str, body: ProduceRequest):
        e = entry(sid)

        def run():
            with Renderer() as r:
                first = e.session.produce(r)
                return outcome(e, *e.session.refine(r, first, max_rounds=body.rounds))
        return start(e, "produce", run)

    @app.post("/api/sessions/{sid}/feedback")
    def feedback(sid: str, body: FeedbackRequest):
        e = entry(sid)
        if not body.text.strip():
            raise HTTPException(400, "feedback is empty")

        def run():
            with Renderer() as r:
                return outcome(e, *e.session.feedback(r, body.text, max_rounds=body.rounds))
        return start(e, "feedback", run)

    @app.post("/api/sessions/{sid}/undo")
    def undo(sid: str):
        e = entry(sid)

        def run():
            with Renderer() as r:
                e.session.undo(r)
            return e.session.summary()
        return start(e, "undo", run)

    @app.post("/api/sessions/{sid}/redo")
    def redo(sid: str):
        e = entry(sid)

        def run():
            with Renderer() as r:
                e.session.redo(r)
            return e.session.summary()
        return start(e, "redo", run)

    @app.post("/api/sessions/{sid}/export")
    def export(sid: str, body: ExportRequest):
        e = entry(sid)
        try:
            path = e.session.export(workspace / "exports", approved=body.approved)
        except PermissionError as err:
            raise HTTPException(403, str(err))
        return {"exported": str(path)}

    # --- manual mode ------------------------------------------------------------------------
    @app.post("/api/sessions/{sid}/prompt")
    def prompt(sid: str, body: PromptRequest):
        e = entry(sid)
        if body.target not in TARGETS:
            raise HTTPException(400, "unknown target")

        def run():
            fp, path = e.session.manual_prompt(body.target)
            return {"prompt": fp.model_dump(), "markdown": path.read_text(), "file": path.name}
        return start(e, "prompt", run)

    @app.post("/api/sessions/{sid}/revise")
    def revise(sid: str, body: ReviseRequest):
        e = entry(sid)
        try:
            data = base64.b64decode(body.image_base64, validate=True)
        except ValueError:
            raise HTTPException(400, "image is not valid base64")
        if len(data) > MAX_UPLOAD:
            raise HTTPException(413, "image is larger than 15 MB")

        def run():
            rev, path = e.session.revise(data, body.note)
            return {"revision": rev.model_dump(), "markdown": path.read_text(), "file": path.name}
        return start(e, "revise", run)

    # --- jobs and files -------------------------------------------------------------------------
    @app.get("/api/jobs/{jid}")
    def job(jid: str):
        j = jobs.get(jid)
        if j is None:
            raise HTTPException(404, "no such job")
        return {"status": j.status, "kind": j.kind, "result": j.result, "error": j.error}

    @app.get("/api/sessions/{sid}/progress/{jid}")
    def progress(sid: str, jid: str):
        e, j = entry(sid), jobs.get(jid)
        if j is None:
            raise HTTPException(404, "no such job")
        events = e.session.log.read()[j.events_at_start:]
        return {"steps": [ev["kind"] + (f": {ev['part']}" if "part" in ev else "") for ev in events],
                "spent": round(e.session.llm.spent, 4)}

    @app.get("/api/sessions/{sid}/files/{name}")
    def file(sid: str, name: str):
        e = entry(sid)
        if not SAFE_FILE.match(name):
            raise HTTPException(404, "not found")
        path = e.session.dir / name
        if not path.exists():
            raise HTTPException(404, "not found")
        return FileResponse(path)

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


def serve(workspace: Path, port: int = 8765, backend: str = DEFAULT_BACKEND) -> None:
    import uvicorn
    print(f"Media director ({backend} backend): http://127.0.0.1:{port}")
    uvicorn.run(create_app(workspace, backend=backend), host="127.0.0.1", port=port, log_level="warning")
