# Teaching UI

A zero-dependency web console for running the demos and the quiz in front of a class.
Built on Python's standard-library `http.server` — **no pip install required**.

```bash
python3 run_all.py ui            # then open http://127.0.0.1:8000
# or directly, with options:
python3 ui/server.py --port 9000 --host 0.0.0.0
```

> `--host 0.0.0.0` lets others on your network open it too (handy for a shared screen).

## What it does

- **Sidebar** lists every demo grouped by domain, plus the 6 scenarios and exam tools.
  Each item shows a one-line summary pulled from the file's docstring.
- **Run** executes the selected demo on the server and renders its output, with the
  `✗ anti-pattern`, `✓ root-cause fix`, and `★ exam tip` blocks highlighted, code boxes
  preserved, and section headers colored.
- **Quiz tab** turns the 12 official sample questions into clickable cards that grade
  instantly, explain why the distractors fail, and keep a running score — ideal for
  letting a room vote before you reveal the answer.

## Live vs simulated

The badge in the top-right shows the mode. If `ANTHROPIC_API_KEY` is set in the
environment that launches the server, model-calling demos hit the real Claude API;
otherwise everything runs in simulated mode. The teaching content is identical either way.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install -r requirements.txt    # only needed for live model calls
python3 run_all.py ui
```

## Offline snapshot (no server)

To share the UI without running anything — e.g. email it, or open on a machine without the
repo — generate a single self-contained HTML file with every demo pre-run and embedded and
the quiz fully interactive:

```bash
python3 ui/snapshot.py                 # -> ui/snapshot.html
python3 ui/snapshot.py /tmp/ccarch.html
```

Open the resulting file directly in any browser. (Live API mode still requires the real
server, since the snapshot bakes in simulated output.)

## How it's wired

```
ui/
├── server.py            # stdlib HTTP server: catalog / run / quiz endpoints + static files
├── templates/index.html # single page
└── static/
    ├── style.css
    └── app.js           # sidebar, runner, output renderer, interactive quiz
```

Only files listed in the catalog can be executed (a whitelist), and runs are serialized so
captured output never interleaves. Output is captured as plain text on the server; the
browser applies all styling.
