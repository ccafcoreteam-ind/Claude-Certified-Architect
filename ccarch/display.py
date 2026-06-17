"""Terminal display helpers — make every demo read like a slide in a lesson.

These are deliberately tiny and dependency-free. They use ANSI colours when the
output is a TTY and degrade to plain text otherwise (e.g. when piped to a file or
shown on a projector that mangles colour).
"""

from __future__ import annotations

import os
import sys
import textwrap

_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

_C = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "grey": "\033[90m",
}


def _c(text: str, *styles: str) -> str:
    if not _USE_COLOR:
        return text
    prefix = "".join(_C[s] for s in styles if s in _C)
    return f"{prefix}{text}{_C['reset']}"


def _wrap(text: str, indent: str = "") -> str:
    width = 88
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        out.append(
            textwrap.fill(
                para,
                width=width,
                initial_indent=indent,
                subsequent_indent=indent,
            )
        )
    return "\n".join(out)


def banner(title: str, subtitle: str = "") -> None:
    """A big top-of-screen banner used at the start of a demo file."""
    line = "═" * 90
    print(_c(line, "cyan"))
    print(_c(f"  {title}", "bold", "cyan"))
    if subtitle:
        print(_c(f"  {subtitle}", "cyan"))
    print(_c(line, "cyan"))


def concept(domain: str, task: str, title: str) -> None:
    """Identifies which domain/task/concept the demo teaches."""
    print()
    print(_c(f"┌── {domain}", "bold", "magenta"))
    print(_c(f"│   {task}", "magenta"))
    print(_c(f"└── Concept: {title}", "bold", "magenta"))
    print()


def h1(text: str) -> None:
    print()
    print(_c(f"▼ {text}", "bold", "blue"))


def h2(text: str) -> None:
    print(_c(f"  • {text}", "bold"))


def rule() -> None:
    print(_c("─" * 90, "grey"))


def wrong(text: str) -> None:
    print(_c("  ✗ WRONG / ANTI-PATTERN", "bold", "red"))
    print(_wrap(text, indent="    "))


def right(text: str) -> None:
    print(_c("  ✓ RIGHT / ROOT-CAUSE FIX", "bold", "green"))
    print(_wrap(text, indent="    "))


def tip(text: str) -> None:
    print(_c("  ★ EXAM TIP", "bold", "yellow"))
    print(_c(_wrap(text, indent="    "), "yellow"))


def note(text: str) -> None:
    print(_wrap(text, indent="  "))


def bullet(text: str, marker: str = "-") -> None:
    print(_wrap(text, indent=f"  {marker} ").replace(f"  {marker} ", f"  {marker} ", 1))


def kv(key: str, value: str) -> None:
    print(f"  {_c(key + ':', 'bold')} {value}")


def code(text: str, lang: str = "") -> None:
    label = f" {lang} " if lang else ""
    print(_c(f"  ┌─{label}" + "─" * (60 - len(label)), "grey"))
    for ln in text.strip("\n").split("\n"):
        print(_c("  │ ", "grey") + _c(ln, "cyan"))
    print(_c("  └" + "─" * 61, "grey"))


def pause(label: str = "next") -> None:
    """In an interactive teaching session, wait for ENTER between steps.

    Set CCARCH_NONSTOP=1 (run_all.py does this) to skip pauses for a full run.
    """
    if os.environ.get("CCARCH_NONSTOP"):
        return
    if not sys.stdin.isatty():
        return
    try:
        input(_c(f"    [press ENTER for {label}]", "dim"))
    except (EOFError, KeyboardInterrupt):
        print()
