# Connecting the Exam Prep Console to your repository

This console can run in two modes:

| Mode | What "Run" shows | Needs |
|------|------------------|-------|
| **Simulated** (default, works anywhere) | Short hand-written summaries baked into `assets/data.js` | nothing — open the HTML file |
| **Live** | The **real** stdout of your repo's demo files (full boxed output, code examples, real titles) | run `api_server.py` from inside the repo |

The frontend tries Live first and silently falls back to Simulated if no
backend is reachable, so it never breaks.

---

## Files in this bundle

```
index.html          ← the console (served at / by api_server.py)
api_server.py       ← zero-dependency server: serves the UI + runs your demos
assets/
  styles.css
  config.js         ← live on/off + API base URL
  data.js           ← teaching copy + simulated fallback output
  app.jsx
```

## Step 1 — Place the files in your repo

Copy `index.html`, `api_server.py`, and the whole `assets/` folder into your
`Claude-Certified-Architect` checkout. Either location works — the server
walks up to find the folder that contains `domains/`:

```
Claude-Certified-Architect/
├── domains/            (your existing demos)
├── scenarios/
├── index.html          ← add
├── api_server.py       ← add
└── assets/             ← add
```

(If you'd rather keep it under `ui/`, drop all three there instead — it still
finds `domains/` one level up.)

## Step 2 — Run it

```bash
python3 api_server.py                       # http://127.0.0.1:8000
python3 api_server.py --host 0.0.0.0 --port 9000   # share on your network

# to make the model-calling demos hit the real API, export your key first:
export ANTHROPIC_API_KEY=sk-ant-...
python3 api_server.py
```

Open the printed URL. Click **Run demo** on any task — the console badge flips
to **● live** and shows the actual output of
`domains/<domain>/task<X>_<Y>_*.py` (run with `CCARCH_NONSTOP=1`, exactly like
`run_all.py`).

Sanity-check what it can find:

```
curl http://127.0.0.1:8000/api/manifest      # lists discovered task ids
curl "http://127.0.0.1:8000/api/run?task=2.4" # the JSON the console renders
```

## Step 3 (optional) — Use your existing `ui/server.py` instead

If you'd rather not run a second server, you only need to add ONE route to
your existing `ui/server.py` and serve `index.html` + `assets/` from it. The
console calls:

```
GET /api/run?task=<id>      ->  { "ok": true, "lines": [ {"type","text"}, ... ] }
```

where `type` is one of `info | cmd | dim | bad | good | tip`. Copy the
`classify()` and `run_file()` helpers from `api_server.py` — they turn a demo's
stdout into that shape. Then point `assets/config.js`'s `apiBase` at your
server if it's on a different origin.

## How the wiring works (in `assets/`)

- **`config.js`** — `live: true/false`, `apiBase`, and the `runUrl(id)` builder.
- **`app.jsx` → `Console`** — on Run, `fetch(CCA_CONFIG.runUrl(task.id))`; if it
  returns `{lines}` it streams those (badge: live); otherwise it streams the
  simulated lines from `data.js` (badge: simulated).

## Note on titles

The simulated copy in `data.js` was written before seeing your source, so a few
task **titles** differ from your repo (e.g. this lists 2.4 as "Structured Tool
Errors"; your repo calls it "MCP Integration"). In Live mode the **run output**
is 100% your repo. If you want the sidebar titles/concepts to match exactly too,
share `domains/` (or connect GitHub) and I'll regenerate `data.js` from source.
