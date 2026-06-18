/* CCA Teaching Console — app */
const { useState, useEffect, useRef, useCallback } = React;
const CCA = window.CCA;

/* ---------- small helpers ---------- */
function useLocal(key, init) {
  const [v, setV] = useState(() => {
    try { const s = localStorage.getItem(key); return s != null ? JSON.parse(s) : init; }
    catch { return init; }
  });
  useEffect(() => { try { localStorage.setItem(key, JSON.stringify(v)); } catch {} }, [key, v]);
  return [v, setV];
}

const Icon = {
  grid: "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
  layers: "M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5",
  book: "M4 4h13a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3V4zM4 4v13a3 3 0 0 0 3 3",
  sun: "M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10zM12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4",
  moon: "M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z",
  play: "M7 4l13 8-13 8z",
  arrow: "M5 12h14M13 6l6 6-6 6",
  check: "M20 6 9 17l-5-5",
  chevron: "M9 6l6 6-6 6",
};
function Svg({ d, size = 16, sw = 1.8, fill = "none", cls }) {
  return (
    <svg className={cls} width={size} height={size} viewBox="0 0 24 24" fill={fill}
      stroke="currentColor" strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round">
      {d.split("M").filter(Boolean).map((seg, i) => <path key={i} d={"M" + seg} />)}
    </svg>
  );
}

/* ---------- Console runner ----------
   Calls the live backend (api_server.py) to run the real repo demo, and falls
   back to the simulated output in data.js when no server is reachable. */
function Console({ task, autorun }) {
  const [shown, setShown] = useState([]);
  const [running, setRunning] = useState(false);
  const [source, setSource] = useState(null); // 'live' | 'simulated' | null
  const lastLines = useRef([]);
  const timers = useRef([]);
  const clearTimers = () => { timers.current.forEach(clearTimeout); timers.current = []; };

  const stream = (lines, step) => {
    clearTimers();
    lastLines.current = lines;
    setShown([]); setRunning(true);
    lines.forEach((line, i) => {
      timers.current.push(setTimeout(() => {
        setShown((s) => [...s, line]);
        if (i === lines.length - 1) setRunning(false);
      }, 100 + i * step));
    });
  };

  const run = useCallback(async () => {
    const cfg = window.CCA_CONFIG || {};
    if (cfg.live) {
      clearTimers(); setShown([]); setRunning(true); setSource(null);
      try {
        const res = await fetch(cfg.runUrl(task.id), { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          if (data && Array.isArray(data.lines) && data.lines.length) {
            setSource("live");
            const n = data.lines.length;
            stream(data.lines, Math.max(6, Math.min(50, Math.round(1400 / n))));
            return;
          }
        }
      } catch (e) { /* fall through to simulated */ }
    }
    setSource("simulated");
    stream(task.output, 230);
  }, [task]);

  const showAll = () => {
    clearTimers();
    setShown(lastLines.current.length ? lastLines.current : task.output);
    if (!source) setSource("simulated");
    setRunning(false);
  };
  const reset = () => { clearTimers(); setShown([]); setRunning(false); setSource(null); lastLines.current = []; };

  useEffect(() => { reset(); if (autorun) run(); /* eslint-disable-next-line */ }, [task.id]);
  useEffect(() => () => clearTimers(), []);

  const glyph = (t) => (t === "bad" ? "✗" : t === "good" ? "✓" : t === "tip" ? "★" : "");
  return (
    <div className="console">
      <div className="console-bar">
        <span className="tl r"></span><span className="tl y"></span><span className="tl g"></span>
        <span className="console-name mono">{CCA.domainById[task.d].folder}task{task.id.replace(".", "_")}.py</span>
        {source && <span className={"src-badge " + source} title={source === "live" ? "Output from running the real demo file" : "Simulated output (no backend reachable)"}>{source === "live" ? "● live" : "○ simulated"}</span>}
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" style={{ height: 30, padding: "0 11px", fontSize: 12 }} onClick={running ? reset : run}>
            <Svg d={Icon.play} size={13} /> {running ? "Running…" : shown.length ? "Run again" : "Run demo"}
          </button>
          <button className="btn btn-ghost" style={{ height: 30, padding: "0 11px", fontSize: 12 }} onClick={showAll} title="Reveal full output">Reveal all</button>
        </div>
      </div>
      <div className="console-body">
        {shown.length === 0 && !running && (
          <div className="cl cl-dim">{"// press Run demo to execute domains/" + CCA.domainById[task.d].folder + "task" + task.id.replace(".", "_") + "_*.py"}</div>
        )}
        {shown.map((line, i) => {
          const g = glyph(line.type);
          return (
            <div key={i} className={"cl cl-" + line.type}>
              {g && <span className="cl-glyph">{g}</span>}
              <span>{line.text}</span>
            </div>
          );
        })}
        {running && <div className="cl"><span className="cursor"></span></div>}
      </div>
    </div>
  );
}

/* ---------- Inline quiz ---------- */
function Quiz({ q, onGoTask }) {
  const [picked, setPicked] = useState(null);
  const keys = ["A", "B", "C", "D"];
  return (
    <div>
      <div className="qlink" style={{ cursor: "default", background: "transparent", borderColor: "var(--border)" }}>
        <div className="qmeta">
          <span className="qtag">{q.id.toUpperCase()}</span>
          <span className="pill">Task {q.task}</span>
        </div>
        <p className="qp" style={{ fontSize: 14, marginBottom: 12 }}>{q.prompt}</p>
        {q.options.map((opt, i) => {
          let cls = "qopt";
          if (picked != null) {
            if (i === q.answer) cls += " correct";
            else if (i === picked) cls += " wrong";
          }
          return (
            <button key={i} className={cls} disabled={picked != null} onClick={() => setPicked(i)}>
              <span className="qk">{keys[i]}</span>
              <span>{opt}</span>
              {picked != null && i === q.answer && <Svg d={Icon.check} size={15} cls="" />}
            </button>
          );
        })}
        {picked != null && (
          <div className="explain">
            <b>{picked === q.answer ? "Correct. " : "Not quite. "}</b>{q.why}
            {onGoTask && <button className="link-row" style={{ marginTop: 10 }} onClick={() => onGoTask(q.task)}>
              <span className="lid">{q.task}</span>
              <span className="ltxt">Open the demo that teaches this</span>
              <Svg d={Icon.arrow} size={14} cls="larr" />
            </button>}
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------- Dashboard ---------- */
function Dashboard({ progress, goDomain, goTask }) {
  const covered = (d) => CCA.tasks.filter((t) => t.d === d.id && progress[t.id]).length;
  const total = (d) => CCA.tasks.filter((t) => t.d === d.id).length;
  const allCovered = Object.values(progress).filter(Boolean).length;
  return (
    <div className="page">
      <span className="eyebrow">Foundations · Teaching Console</span>
      <h1 className="h1" style={{ marginTop: 10 }}>Claude Certified Architect</h1>
      <p className="lede">A runnable companion to the Foundations exam — every concept is a small demo you can project, step through, and discuss. Five domains, thirty task demos, six end-to-end scenarios.</p>

      <div className="spacer-l"></div>
      <div className="stat-row">
        <div className="card stat"><div className="n accent mono">5</div><div className="k">Domains</div></div>
        <div className="card stat"><div className="n mono">30</div><div className="k">Task demos</div></div>
        <div className="card stat"><div className="n mono">6</div><div className="k">Scenarios</div></div>
        <div className="card stat"><div className="n mono">{allCovered}<span style={{ fontSize: 16, color: "var(--text-faint)" }}>/30</span></div><div className="k">Covered in class</div></div>
      </div>

      <div className="spacer-l"></div>
      <div className="row-between" style={{ marginBottom: 14 }}>
        <h2 className="section-title"><span className="nav-dot" style={{ background: "var(--accent)" }}></span>The five domains</h2>
        <span className="mono" style={{ fontSize: 11.5, color: "var(--text-faint)" }}>click a card to teach it</span>
      </div>
      <div className="grid-domains">
        {CCA.domains.map((d) => {
          const c = covered(d), tt = total(d);
          return (
            <div key={d.id} className="card dcard" onClick={() => goDomain(d.id)}>
              <div className="dcard-top">
                <div className="dcard-num">{d.n}</div>
                <div style={{ minWidth: 0 }}>
                  <h3>{d.title}</h3>
                  <p className="blurb">{d.blurb}</p>
                </div>
              </div>
              <div>
                <div className="row-between" style={{ marginBottom: 6 }}>
                  <span className="mono" style={{ fontSize: 11, color: "var(--text-faint)" }}>exam weight</span>
                  <span className="mono" style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)" }}>{d.weight}%</span>
                </div>
                <div className="weightbar"><i style={{ width: d.weight + "%" }}></i></div>
              </div>
              <div className="dcard-foot">
                <span>Tasks {CCA.tasks.filter(t=>t.d===d.id)[0].id}–{CCA.tasks.filter(t=>t.d===d.id).slice(-1)[0].id}</span>
                <span className="prog-mini">
                  <span className="prog-track"><i style={{ width: (tt ? c / tt * 100 : 0) + "%" }}></i></span>
                  {c}/{tt}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="spacer-l"></div>
      <h2 className="section-title" style={{ marginBottom: 14 }}><span className="nav-dot" style={{ background: "var(--accent)" }}></span>Three themes that run through everything</h2>
      <div className="themes">
        {CCA.themes.map((t, i) => (
          <div key={t.id} className="card theme">
            <div className="tnum">{String(i + 1).padStart(2, "0")}</div>
            <h4>{t.title}</h4>
            <p>{t.body}</p>
          </div>
        ))}
      </div>
      <div className="spacer-m"></div>
      <div className="card" style={{ padding: "16px 20px", display: "flex", gap: 12, alignItems: "center" }}>
        <span className="pill accent">tip</span>
        <p style={{ margin: 0, fontSize: 13.5, color: "var(--text-soft)" }}>
          The exam's underlying question is always: <b style={{ color: "var(--text)" }}>what is the simplest mechanism that reliably fixes the actual root cause?</b>
        </p>
      </div>
    </div>
  );
}

/* ---------- Demo (task) view ---------- */
function DemoView({ task, progress, setCovered, goTask }) {
  const domain = CCA.domainById[task.d];
  const domainTasks = CCA.tasks.filter((t) => t.d === task.d);
  const idx = domainTasks.findIndex((t) => t.id === task.id);
  const isCovered = !!progress[task.id];
  const linkedQs = (task.q || []).map((id) => CCA.questionById[id]).filter(Boolean);

  return (
    <div className="page page-wide">
      <div className="row-between" style={{ marginBottom: 18 }}>
        <div>
          <span className="eyebrow">{domain.title} · Task {task.id}</span>
          <h1 className="h1" style={{ marginTop: 8 }}>{task.title}</h1>
        </div>
        <button className={"btn " + (isCovered ? "btn-primary" : "btn-ghost")} onClick={() => setCovered(task.id, !isCovered)}>
          <Svg d={Icon.check} size={15} /> {isCovered ? "Covered" : "Mark covered"}
        </button>
      </div>

      <div className="demo-layout">
        <div className="demo-main">
          <div className="card concept">
            <span className="eyebrow" style={{ marginBottom: 8, display: "block" }}>Concept</span>
            <p>{task.concept}</p>
          </div>

          <Console task={task} />

          <div className="compare">
            <div className="cmp bad">
              <div className="lbl"><span>✗</span> Anti-pattern</div>
              <p>{task.antipattern}</p>
            </div>
            <div className="cmp good">
              <div className="lbl"><span>✓</span> The right way</div>
              <p>{task.right}</p>
            </div>
          </div>

          <div className="tipbar">
            <span className="star">★</span>
            <p><b>Exam tip</b>{task.tip}</p>
          </div>

          <div className="row-between" style={{ marginTop: 6 }}>
            <button className="btn btn-ghost" disabled={idx === 0} style={{ opacity: idx === 0 ? 0.4 : 1 }}
              onClick={() => idx > 0 && goTask(domainTasks[idx - 1].id)}>
              <Svg d={Icon.arrow} size={14} cls="" /> <span style={{ transform: "scaleX(-1)", display: "inline-block" }}></span>Previous
            </button>
            <span className="mono" style={{ fontSize: 12, color: "var(--text-faint)" }}>{idx + 1} / {domainTasks.length} in Domain {domain.n}</span>
            <button className="btn btn-ghost" disabled={idx === domainTasks.length - 1} style={{ opacity: idx === domainTasks.length - 1 ? 0.4 : 1 }}
              onClick={() => idx < domainTasks.length - 1 && goTask(domainTasks[idx + 1].id)}>
              Next <Svg d={Icon.arrow} size={14} />
            </button>
          </div>
        </div>

        <div className="demo-side">
          {linkedQs.length > 0 && (
            <div className="card side-card">
              <h5>Linked exam questions</h5>
              {linkedQs.map((q) => <Quiz key={q.id} q={q} onGoTask={goTask} />)}
            </div>
          )}
          {task.links && task.links.length > 0 && (
            <div className="card side-card">
              <h5>Related concepts</h5>
              {task.links.map((id) => {
                const t = CCA.taskById[id];
                if (!t) return null;
                return (
                  <button key={id} className="link-row" onClick={() => goTask(id)}>
                    <span className="lid">{id}</span>
                    <span className="ltxt">{t.title}</span>
                    <Svg d={Icon.arrow} size={14} cls="larr" />
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- Scenarios ---------- */
function Scenarios({ goTask }) {
  return (
    <div className="page">
      <span className="eyebrow">End-to-end</span>
      <h1 className="h1" style={{ marginTop: 10 }}>Six runnable scenarios</h1>
      <p className="lede">Fuller systems that compose the task concepts — a real support agent, a multi-agent research pipeline, an extraction pipeline, and more. Each step links to the demo that teaches it.</p>
      <div className="spacer-l"></div>
      {CCA.scenarios.map((s) => (
        <div key={s.id} className="card scn">
          <div className="scn-head">
            <div className="scn-n">{s.n}</div>
            <div>
              <h3>{s.title}</h3>
              <p>{s.summary}</p>
              <div className="scn-dtags">
                {s.domains.map((d) => <span key={d} className="pill">D{CCA.domainById[d].n} · {CCA.domainById[d].short}</span>)}
              </div>
            </div>
          </div>
          <div className="steps">
            {s.steps.map((st, i) => (
              <div key={i} className="step">
                <div className="sdot">{i + 1}</div>
                <div className="stxt"><b>{st.t}</b><span>{st.d}</span></div>
                <button className="slink" onClick={() => goTask(st.task)}>task {st.task} →</button>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ---------- Cheat sheet ---------- */
function CheatSheet({ goTask }) {
  return (
    <div className="page">
      <span className="eyebrow">High-yield</span>
      <h1 className="h1" style={{ marginTop: 10 }}>Cheat sheet</h1>
      <p className="lede">The facts to memorise, grouped by domain. Every line points to the demo that proves it — jump there to teach it live.</p>
      <div className="spacer-l"></div>
      {CCA.domains.map((d) => {
        const items = CCA.cheat.filter((c) => c.d === d.id);
        if (!items.length) return null;
        return (
          <div key={d.id} className="cheat-group">
            <h3>
              <span className="dcard-num" style={{ width: 26, height: 26, fontSize: 12, borderRadius: 7 }}>{d.n}</span>
              {d.title}
              <span className="cg-w">{d.weight}%</span>
            </h3>
            <div className="cheat-list">
              {items.map((c, i) => (
                <div key={i} className="card cheat-item">
                  <span className="ci-mark">→</span>
                  <span className="ci-fact">{c.fact}</span>
                  <button className="ci-link" onClick={() => goTask(c.task)}>task {c.task}</button>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ---------- Sidebar ---------- */
function Sidebar({ route, goto, goTask, progress }) {
  const [open, setOpen] = useState(() => ({ [route.taskId ? CCA.taskById[route.taskId]?.d : "d1"]: true }));
  const toggle = (id) => setOpen((o) => ({ ...o, [id]: !o[id] }));
  const top = [
    { v: "dashboard", label: "Dashboard", icon: Icon.grid, key: "1" },
    { v: "scenarios", label: "Scenarios", icon: Icon.layers, key: "2" },
    { v: "cheat", label: "Cheat sheet", icon: Icon.book, key: "3" },
  ];
  return (
    <aside className="sidebar">
      <div className="sb-head">
        <div className="brand">
          <div className="brand-mark">CC</div>
          <div className="brand-txt"><b>Architect Console</b><span>foundations · teaching</span></div>
        </div>
      </div>
      <nav className="sb-nav">
        <div className="nav-group">
          {top.map((t) => (
            <button key={t.v} className={"nav-item" + (route.view === t.v ? " active" : "")} onClick={() => goto({ view: t.v })}>
              <Svg d={t.icon} size={16} /> {t.label}
              <span className="nav-key">{t.key}</span>
            </button>
          ))}
        </div>
        <div className="nav-group">
          <div className="nav-label">Domains</div>
          <div className="dnav">
            {CCA.domains.map((d) => {
              const tasks = CCA.tasks.filter((t) => t.d === d.id);
              const isOpen = open[d.id];
              return (
                <div key={d.id}>
                  <button className={"dnav-row" + (route.view === "demo" && CCA.taskById[route.taskId]?.d === d.id ? " active" : "")} onClick={() => toggle(d.id)}>
                    <span className="dnum">{d.n}</span>
                    <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d.short}</span>
                    <Svg d={Icon.chevron} size={14} cls="" />
                    <span style={{ display: "none" }}>{isOpen}</span>
                  </button>
                  {isOpen && (
                    <div style={{ padding: "2px 0 6px 8px" }}>
                      {tasks.map((t) => (
                        <button key={t.id} className={"nav-item" + (route.taskId === t.id ? " active" : "")}
                          style={{ padding: "6px 10px", fontSize: 12.5 }} onClick={() => goTask(t.id)}>
                          <span className="nav-dot" style={{ background: progress[t.id] ? "var(--good)" : undefined }}></span>
                          <span className="mono" style={{ fontSize: 11.5, color: "var(--text-faint)", width: 24 }}>{t.id}</span>
                          <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.title}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </nav>
      <div className="sb-foot">
        <div className="mono" style={{ fontSize: 11, color: "var(--text-faint)", lineHeight: 1.6 }}>
          python3 run_all.py ui<br />→ 127.0.0.1:8000
        </div>
      </div>
    </aside>
  );
}

/* ---------- App ---------- */
function App() {
  const [theme, setTheme] = useLocal("cca-theme", "light");
  const [route, setRoute] = useLocal("cca-route", { view: "dashboard", taskId: null });
  const [progress, setProgress] = useLocal("cca-progress", {});
  const scrollRef = useRef(null);

  useEffect(() => { document.documentElement.setAttribute("data-theme", theme); }, [theme]);
  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = 0; }, [route]);

  const goto = (r) => setRoute({ taskId: null, ...r });
  const goTask = (id) => setRoute({ view: "demo", taskId: id });
  const goDomain = (id) => goTask(CCA.tasks.filter((t) => t.d === id)[0].id);
  const setCovered = (id, val) => setProgress((p) => ({ ...p, [id]: val }));

  // keyboard nav
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
      if (e.key === "1") goto({ view: "dashboard" });
      else if (e.key === "2") goto({ view: "scenarios" });
      else if (e.key === "3") goto({ view: "cheat" });
      else if (e.key.toLowerCase() === "t") setTheme((t) => (t === "light" ? "dark" : "light"));
      else if ((e.key === "ArrowRight" || e.key === "ArrowLeft") && route.view === "demo") {
        const t = CCA.taskById[route.taskId];
        const list = CCA.tasks.filter((x) => x.d === t.d);
        const i = list.findIndex((x) => x.id === t.id);
        const ni = e.key === "ArrowRight" ? Math.min(i + 1, list.length - 1) : Math.max(i - 1, 0);
        goTask(list[ni].id);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [route]);

  const task = route.taskId ? CCA.taskById[route.taskId] : null;
  const crumbLabel = route.view === "demo" && task
    ? <><b>{CCA.domainById[task.d].short}</b><span className="crumb-sep">/</span><span>Task {task.id}</span></>
    : <b>{route.view === "dashboard" ? "Dashboard" : route.view === "scenarios" ? "Scenarios" : "Cheat sheet"}</b>;

  return (
    <div className="shell">
      <Sidebar route={route} goto={goto} goTask={goTask} progress={progress} />
      <div className="main">
        <div className="topbar">
          <div className="crumbs">
            <span style={{ color: "var(--text-faint)" }}>console</span>
            <span className="crumb-sep">/</span>
            {crumbLabel}
          </div>
          <div className="topbar-spacer"></div>
          <span className="kbd">←/→</span><span style={{ fontSize: 11.5, color: "var(--text-faint)" }}>step</span>
          <button className="tb-btn" onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
            <Svg d={theme === "light" ? Icon.moon : Icon.sun} size={15} cls="tb-icon" />
            {theme === "light" ? "Dark" : "Light"}
          </button>
        </div>
        <div className="scroll app-bg" ref={scrollRef}>
          {route.view === "dashboard" && <Dashboard progress={progress} goDomain={goDomain} goTask={goTask} />}
          {route.view === "demo" && task && <DemoView task={task} progress={progress} setCovered={setCovered} goTask={goTask} />}
          {route.view === "scenarios" && <Scenarios goTask={goTask} />}
          {route.view === "cheat" && <CheatSheet goTask={goTask} />}
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
