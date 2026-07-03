# Contributing

Thanks for considering a contribution to this teaching codebase! Small, focused changes
are especially welcome — a typo fix, a clearer sentence, a missing demo case.

## Quick workflow

1. **Fork** the repo (top-right "Fork" button on GitHub).
2. **Clone your fork** and add this repo as `upstream`:
   ```bash
   git clone https://github.com/<your-username>/Claude-Certified-Architect.git
   cd Claude-Certified-Architect
   git remote add upstream https://github.com/jacinthpaul/Claude-Certified-Architect.git
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b my-fix
   ```
4. **Make your change.** For code changes, run the smoke test before opening a PR:
   ```bash
   python3 run_all.py --check    # should print ALL PASS
   ```
5. **Commit and push** to your fork:
   ```bash
   git commit -am "Describe your change"
   git push origin my-fix
   ```
6. **Open a pull request** from your branch into this repo's default branch.

## What makes a good PR here

- Keep it small and focused — one idea per PR is easier to review and merge.
- Match the existing style: demos are self-contained, deterministic by default (no API
  key required), and explain *why*, not just *what*.
- Docs changes should stay consistent with the teaching tone used throughout the README
  and `teaching/teaching_guide.md`.

## Questions

Open an issue if you're not sure whether a change fits — happy to discuss before you put
in the work.
