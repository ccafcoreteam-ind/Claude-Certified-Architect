"use strict";

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, txt) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (txt != null) e.textContent = txt;
  return e;
};
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

let current = null; // currently selected demo {path,title,summary}

/* ----------------------------------------------------------------------- */
/* Boot                                                                     */
/* ----------------------------------------------------------------------- */
async function boot() {
  const cat = await fetch("/api/catalog").then((r) => r.json());
  const badge = $("#mode-badge");
  badge.textContent = "mode: " + cat.mode;
  badge.classList.add(cat.mode);
  renderNav(cat.groups);

  $("#tab-demos").onclick = () => switchTab("demos");
  $("#tab-quiz").onclick = () => switchTab("quiz");
  $("#run-btn").onclick = runCurrent;
}

function switchTab(which) {
  const demos = which === "demos";
  $("#tab-demos").classList.toggle("active", demos);
  $("#tab-quiz").classList.toggle("active", !demos);
  $("#demo-view").hidden = !demos;
  $("#quiz-view").hidden = demos;
  if (which === "demos") renderNav(window.__groups);
  else { renderQuizNavHint(); loadQuiz(); }
}

/* ----------------------------------------------------------------------- */
/* Sidebar                                                                  */
/* ----------------------------------------------------------------------- */
function renderNav(groups) {
  window.__groups = groups;
  const list = $("#nav-list");
  list.innerHTML = "";
  groups.forEach((g) => {
    const grp = el("div", "nav-group");
    grp.appendChild(el("div", "group-label", g.label));
    g.items.forEach((it) => {
      const node = el("div", "nav-item");
      node.appendChild(el("div", "ni-title", it.title));
      if (it.summary) node.appendChild(el("div", "ni-sub", it.summary));
      node.onclick = () => selectDemo(it, node);
      node.dataset.path = it.path;
      grp.appendChild(node);
    });
    list.appendChild(grp);
  });
}

function renderQuizNavHint() {
  const list = $("#nav-list");
  list.innerHTML = "";
  const box = el("div", "nav-group");
  box.appendChild(el("div", "group-label", "Quiz"));
  const p = el("div", "nav-item");
  p.appendChild(el("div", "ni-title", "12 sample questions"));
  p.appendChild(el("div", "ni-sub",
    "Click an answer to grade it. Each is tagged with its domain/task and the demo that shows the concept."));
  box.appendChild(p);
  list.appendChild(box);
}

function selectDemo(it, node) {
  current = it;
  document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));
  node.classList.add("active");
  $("#demo-title").textContent = it.title;
  $("#demo-summary").textContent = it.summary || "";
  $("#run-btn").disabled = false;
  $("#output").innerHTML = '<div class="placeholder muted">Press ▶ Run to execute <code>' +
    esc(it.path) + "</code>.</div>";
}

/* ----------------------------------------------------------------------- */
/* Run a demo + render output                                               */
/* ----------------------------------------------------------------------- */
async function runCurrent() {
  if (!current) return;
  const btn = $("#run-btn");
  const out = $("#output");
  btn.disabled = true; btn.classList.add("running"); btn.textContent = "⏳ Running…";
  out.innerHTML = '<div class="placeholder muted">Running…</div>';
  try {
    const res = await fetch("/api/run", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ module: current.path }),
    }).then((r) => r.json());
    out.innerHTML = renderOutput(res.output || "(no output)");
  } catch (e) {
    out.innerHTML = '<div class="block wrong">Failed to run: ' + esc(String(e)) + "</div>";
  } finally {
    btn.disabled = false; btn.classList.remove("running"); btn.textContent = "▶ Run";
  }
}

/*
  Turn the demo's plain-text output into styled HTML. The CLI markers are stable:
    line of '='            -> title banner border
    '┌── ' / '│' / '└── '  -> concept banner
    '▼ '                   -> section header
    '  • '                 -> sub header
    '  ✗ WRONG...'         -> red block (consumes following 4-space-indented lines)
    '  ✓ RIGHT...'         -> green block
    '  ★ EXAM TIP'         -> amber block
    '  ┌─ ... ┐'/'│'/'└─'  -> code box
    line of '─'            -> rule
*/
function renderOutput(text) {
  const lines = text.replace(/ /g, " ").split("\n");
  let html = "";
  let i = 0;

  const indentedFollow = () => {
    const collected = [];
    while (i + 1 < lines.length && /^\s{4}\S/.test(lines[i + 1])) {
      collected.push(lines[++i].replace(/^\s{4}/, ""));
    }
    return collected.join("\n");
  };

  while (i < lines.length) {
    const ln = lines[i];
    const trimmed = ln.trim();

    if (/^[═]+$/.test(trimmed)) { html += `<div class="line l-banner">${esc(ln)}</div>`; i++; continue; }
    if (/^[─]{10,}$/.test(trimmed)) { html += `<div class="line l-rule">${esc(ln)}</div>`; i++; continue; }

    if (/^┌──|^│|^└──/.test(ln)) { html += `<div class="line l-concept">${esc(ln)}</div>`; i++; continue; }

    // banner title lines: between two '=' borders, indented by 2 spaces, non-empty
    if (/^ {2}\S/.test(ln) && i > 0 && /^[═]+$/.test(lines[i - 1].trim())) {
      html += `<div class="line l-banner-title">${esc(ln)}</div>`; i++; continue;
    }

    if (/^▼ /.test(trimmed) || /^▼ /.test(ln)) {
      html += `<div class="line l-h1">${esc(ln)}</div>`; i++; continue;
    }
    if (/^ {2}• /.test(ln)) { html += `<div class="line l-h2">${esc(ln)}</div>`; i++; continue; }

    // code box: starts with '  ┌─'
    if (/^ {2}┌─/.test(ln)) {
      const box = [ln];
      while (i + 1 < lines.length && /^ {2}[│└]/.test(lines[i + 1])) box.push(lines[++i]);
      html += `<div class="codebox">${esc(box.join("\n"))}</div>`; i++; continue;
    }

    // marker blocks
    if (/✗ WRONG/.test(ln)) {
      const body = indentedFollow();
      html += block("wrong", "✗ Anti-pattern", body); i++; continue;
    }
    if (/✓ RIGHT/.test(ln)) {
      const body = indentedFollow();
      html += block("right", "✓ Root-cause fix", body); i++; continue;
    }
    if (/★ EXAM TIP/.test(ln)) {
      const body = indentedFollow();
      html += block("tip", "★ Exam tip", body); i++; continue;
    }

    // key: value lines  ('  key: value')
    const kv = ln.match(/^(\s{2,})([^:]{1,40}):\s(.*)$/);
    if (kv && !/^\s*[┌│└]/.test(ln)) {
      html += `<div class="line">${esc(kv[1])}<span class="l-kv-key">${esc(kv[2])}:</span> ${esc(kv[3])}</div>`;
      i++; continue;
    }

    html += `<div class="line">${esc(ln) || "&nbsp;"}</div>`;
    i++;
  }
  return html;
}

function block(kind, label, body) {
  return `<div class="block ${kind}"><span class="blabel">${label}</span>${esc(body)}</div>`;
}

/* ----------------------------------------------------------------------- */
/* Quiz                                                                     */
/* ----------------------------------------------------------------------- */
let quizState = { score: 0, answered: 0 };

async function loadQuiz() {
  const list = $("#quiz-list");
  if (list.dataset.loaded) return;
  const qs = await fetch("/api/quiz").then((r) => r.json());
  list.innerHTML = "";
  quizState = { score: 0, answered: 0 };
  updateScore();
  qs.forEach((q) => list.appendChild(renderQuestion(q)));
  list.dataset.loaded = "1";
}

function renderQuestion(q) {
  const card = el("div", "q-card");
  card.appendChild(el("div", "q-meta", `Q${q.n} · ${q.scenario}  ·  ${q.maps}`));
  card.appendChild(el("div", "q-text", q.q));
  const opts = el("div", "q-options");
  const buttons = {};
  ["A", "B", "C", "D"].forEach((k) => {
    const b = el("button", "q-opt");
    b.innerHTML = `<span class="opt-key">${k}</span>${esc(q.options[k])}`;
    b.onclick = () => answer(q, k, buttons, why);
    buttons[k] = b;
    opts.appendChild(b);
  });
  card.appendChild(opts);
  const why = el("div", "q-why");
  why.hidden = true;
  card.appendChild(why);
  return card;
}

function answer(q, chosen, buttons, why) {
  if (why.dataset.done) return;
  why.dataset.done = "1";
  Object.entries(buttons).forEach(([k, b]) => {
    b.disabled = true;
    if (k === q.answer) b.classList.add("correct");
    if (k === chosen && chosen !== q.answer) b.classList.add("wrong");
  });
  const ok = chosen === q.answer;
  why.hidden = false;
  why.classList.toggle("miss", !ok);
  why.innerHTML = `<b>${ok ? "Correct" : "Not quite"} — answer ${q.answer}.</b> ` + esc(q.why);
  quizState.answered++;
  if (ok) quizState.score++;
  updateScore();
}

function updateScore() {
  $("#quiz-score").textContent = `score: ${quizState.score} / ${quizState.answered}`;
}

boot();
