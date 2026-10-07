// Media Director UI. Model output is always inserted with textContent, never as HTML.
"use strict";

const $ = (id) => document.getElementById(id);
let sid = null;
let draft = null;
let budget = 0;

// --- helpers ------------------------------------------------------------------------
async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `${res.status} ${res.statusText}`);
  return data;
}

function el(tag, text, cls) {
  const e = document.createElement(tag);
  if (text !== undefined) e.textContent = text;
  if (cls) e.className = cls;
  return e;
}

function list(id, items, fmt) {
  const ul = $(id);
  ul.replaceChildren(...(items || []).map((x) => (fmt ? fmt(x) : el("li", x))));
}

function showError(msg) {
  $("error").textContent = msg;
  $("error").hidden = !msg;
}

function setMeter(spent) {
  $("meter").hidden = false;
  $("spent").textContent = `$${Number(spent || 0).toFixed(2)}`;
  $("budget").textContent = `$${Number(budget).toFixed(2)}`;
}

function busy(on) {
  document.querySelectorAll("button").forEach((b) => { if (!b.dataset.locked) b.disabled = on; });
}

// Start a background job and poll until it finishes, showing progress.
async function run(path, body, title) {
  showError("");
  busy(true);
  $("working").hidden = false;
  $("working-title").textContent = title;
  $("working-steps").replaceChildren();
  try {
    const { job } = await api(path, body);
    for (;;) {
      await new Promise((r) => setTimeout(r, 1500));
      const [j, p] = await Promise.all([api(`/api/jobs/${job}`), api(`/api/sessions/${sid}/progress/${job}`)]);
      list("working-steps", p.steps.slice(-6));
      setMeter(p.spent);
      if (j.status === "done") return j.result;
      if (j.status === "error") throw new Error(j.error);
    }
  } finally {
    $("working").hidden = true;
    busy(false);
  }
}

async function guard(fn) {
  try { await fn(); } catch (e) { showError(e.message); }
}

// --- 1. start ----------------------------------------------------------------------------
$("btn-start").onclick = () => guard(async () => {
  if (!$("consent").checked) throw new Error("Please agree to sending your answers to Claude first.");
  budget = Number($("budget-in").value);
  const s = await api("/api/sessions", { budget });
  sid = s.id;
  await api(`/api/sessions/${sid}/consent`, {});
  setMeter(0);
  $("questions").replaceChildren(...s.questions.map((q, i) => {
    const l = el("label", q);
    const t = el("textarea");
    t.rows = 2; t.id = `q${i}`;
    l.appendChild(t);
    return l;
  }));
  $("target").replaceChildren(...Object.entries(s.targets).map(([k, v]) => {
    const o = el("option", v); o.value = k; return o;
  }));
  $("s-start").querySelectorAll("input, button").forEach((x) => { x.disabled = true; x.dataset.locked = "1"; });
  $("s-interview").hidden = false;
});

// --- 2-3. interview and intent --------------------------------------------------------------
const FIELDS = [["purpose", "Purpose"], ["audience", "Audience"], ["feeling", "Feeling"],
  ["personal_detail", "Personal detail"], ["must_include", "Must include (comma-separated)"],
  ["avoid", "Avoid (comma-separated)"]];

$("btn-intent").onclick = () => guard(async () => {
  const answers = [...$("questions").querySelectorAll("textarea")].map((t) => t.value);
  draft = await run(`/api/sessions/${sid}/intent`, { medium: $("medium").value, answers }, "Reading your answers…");
  $("intent-summary").textContent = draft.summary;
  $("intent-fields").replaceChildren(...FIELDS.map(([k, label]) => {
    const l = el("label", label);
    const v = draft.intent[k];
    const t = el("textarea"); t.rows = 2; t.dataset.key = k;
    t.value = Array.isArray(v) ? v.join(", ") : v;
    l.appendChild(t);
    return l;
  }));
  const qs = draft.intent.open_questions || [];
  $("open-questions").replaceChildren(...(qs.length ? [el("h3", "The director would like to know")] : []),
    ...qs.map((q) => {
      const l = el("label", q);
      const i = el("input"); i.dataset.q = q; i.placeholder = "Your answer (optional)";
      l.appendChild(i);
      return l;
    }));
  $("s-intent").hidden = false;
  $("s-intent").scrollIntoView({ behavior: "smooth" });
});

$("btn-confirm").onclick = () => guard(async () => {
  for (const t of $("intent-fields").querySelectorAll("textarea")) {
    const k = t.dataset.key;
    draft.intent[k] = Array.isArray(draft.intent[k])
      ? t.value.split(",").map((x) => x.trim()).filter(Boolean) : t.value;
  }
  const open_answers = [...$("open-questions").querySelectorAll("input")]
    .map((i) => ({ question: i.dataset.q, answer: i.value }));
  draft.intent.open_questions = [];
  await api(`/api/sessions/${sid}/intent/confirm`, { draft, open_answers });
  if ($("medium").value === "slides") {
    // Automatic mode makes posters only; slides go through manual mode.
    document.querySelector('.tab[data-tab="manual"]').click();
    const auto = document.querySelector('.tab[data-tab="auto"]');
    auto.disabled = true; auto.dataset.locked = "1"; auto.title = "Automatic mode makes posters only";
  }
  $("s-concepts").hidden = false;
  $("s-concepts").scrollIntoView({ behavior: "smooth" });
});

// --- 4. concepts ---------------------------------------------------------------------------
$("btn-concepts").onclick = () => guard(async () => {
  const concepts = await run(`/api/sessions/${sid}/concepts`, {}, "Proposing concepts…");
  $("concepts").replaceChildren(...concepts.map((c, i) => {
    const card = el("div", undefined, "card");
    card.append(el("h3", c.title), el("p", c.idea), el("p", c.why_personal, "meta"),
      el("p", `Mood: ${c.mood}`, "meta"));
    const sw = el("div", undefined, "swatches");
    for (const hex of c.palette) {
      const s = el("span"); s.title = hex;
      if (/^#[0-9a-fA-F]{3,8}$/.test(hex)) s.style.background = hex;
      sw.appendChild(s);
    }
    const b = el("button", "Choose this");
    b.onclick = () => guard(async () => {
      await api(`/api/sessions/${sid}/choose`, { index: i, note: $("concept-note").value });
      [...$("concepts").children].forEach((x, j) => (x.style.opacity = j === i ? 1 : 0.4));
      $("s-make").hidden = false;
      $("s-make").scrollIntoView({ behavior: "smooth" });
    });
    card.append(sw, el("p", c.composition, "meta"), b);
    return card;
  }));
});

// --- 5. make: tabs ------------------------------------------------------------------------------
document.querySelectorAll(".tab").forEach((t) => (t.onclick = () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === t));
  $("tab-auto").hidden = t.dataset.tab !== "auto";
  $("tab-manual").hidden = t.dataset.tab !== "manual";
}));

// --- automatic mode ------------------------------------------------------------------------------
function showOutcome(out) {
  const st = out.state;
  setMeter(st.spent);
  $("result").hidden = false;
  showRenders(st);
  if (out.critique) {
    $("stopped").textContent = out.stopped ? `Stopped: ${out.stopped}` : "";
    list("strengths", out.critique.strengths);
    list("issues", out.critique.issues, (i) => {
      const li = el("li");
      li.append(el("span", `[${i.severity}] `, i.severity === "high" ? "sev-high" : ""),
        el("span", `${i.part}: ${i.problem}`));
      return li;
    });
  }
  const qs = out.questions || [];
  $("ask").hidden = !qs.length;
  list("ask-list", qs);
}

function showRenders(st) {
  if (!st.renders.length) return;
  const last = st.renders[st.renders.length - 1];
  $("render").src = `/api/sessions/${sid}/files/${last}?t=${Date.now()}`;
  $("render-cap").textContent = `${last} · version ${st.cursor + 1} of ${st.versions.length}: ${st.versions[st.cursor] || ""}`;
  $("thumbs").replaceChildren(...st.renders.map((r) => {
    const img = el("img"); img.src = `/api/sessions/${sid}/files/${r}`; img.alt = r; img.title = r;
    if (r === last) img.className = "current";
    img.onclick = () => { $("render").src = img.src; $("render-cap").textContent = r; };
    return img;
  }));
}

$("btn-produce").onclick = () => guard(async () => {
  const out = await run(`/api/sessions/${sid}/produce`, { rounds: Number($("rounds").value) },
    "Making the poster (a few minutes)…");
  showOutcome(out);
});

$("btn-feedback").onclick = () => guard(async () => {
  const text = $("feedback").value.trim();
  if (!text) throw new Error("Write your feedback or answers first.");
  const out = await run(`/api/sessions/${sid}/feedback`, { text, rounds: Number($("rounds").value) },
    "Refining with your feedback…");
  $("feedback").value = "";
  showOutcome(out);
});

for (const [id, path] of [["btn-undo", "undo"], ["btn-redo", "redo"]]) {
  $(id).onclick = () => guard(async () => {
    const st = await run(`/api/sessions/${sid}/${path}`, {}, path === "undo" ? "Undoing…" : "Redoing…");
    showRenders(st);
  });
}

$("btn-export").onclick = () => guard(async () => {
  const ok = window.confirm("Export is irreversible: the poster, its HTML and a provenance file are copied out " +
    "of the workspace to workspace/exports. Export now?");
  if (!ok) return;
  const r = await api(`/api/sessions/${sid}/export`, { approved: true });
  showError("");
  $("stopped").textContent = `Exported to ${r.exported}`;
});

// --- manual mode ----------------------------------------------------------------------------------
function showPrompt(r) {
  $("prompt-out").hidden = false;
  $("prompt-md").textContent = r.markdown;
}

$("btn-prompt").onclick = () => guard(async () => {
  const r = await run(`/api/sessions/${sid}/prompt`, { target: $("target").value }, "Writing your prompt…");
  window.lastPrompt = r.prompt.prompt;
  showPrompt(r);
});

$("btn-copy").onclick = () => guard(async () => {
  await navigator.clipboard.writeText(window.lastPrompt || "");
  $("copied").textContent = "Copied.";
  setTimeout(() => ($("copied").textContent = ""), 2000);
});

$("btn-revise").onclick = () => guard(async () => {
  const f = $("result-file").files[0];
  if (!f) throw new Error("Choose the image your tool produced first.");
  if (f.size > 15 * 1024 * 1024) throw new Error("The image is larger than 15 MB.");
  const b64 = await new Promise((res, rej) => {
    const rd = new FileReader();
    rd.onload = () => res(String(rd.result).split(",")[1]);
    rd.onerror = () => rej(new Error("Could not read the file."));
    rd.readAsDataURL(f);
  });
  const r = await run(`/api/sessions/${sid}/revise`, { image_base64: b64, note: $("result-note").value },
    "Judging your result…");
  $("revision").hidden = false;
  list("rev-works", r.revision.what_works);
  list("rev-misses", r.revision.what_misses_the_intent);
  window.lastPrompt = r.revision.revised.prompt;
  showPrompt(r);
});
