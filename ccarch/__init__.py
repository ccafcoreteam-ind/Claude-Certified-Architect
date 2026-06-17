"""ccarch — the shared toolkit for the Claude Certified Architect teaching codebase.

This package gives every demo a common look-and-feel and a single Claude client
that runs in two modes:

* LIVE mode   - when ANTHROPIC_API_KEY is set and the `anthropic` SDK is installed,
                demos that call the model make real API calls.
* SIMULATED   - otherwise, demos fall back to a clearly-labelled deterministic
                simulation so the whole codebase still runs in a classroom with
                no setup and no network.

Either way the *teaching points* (the architecture, the exam tips, the
anti-patterns) are identical — they are baked into the code, not the model.
"""

from .display import (
    banner,
    concept,
    h1,
    h2,
    rule,
    wrong,
    right,
    tip,
    note,
    kv,
    bullet,
    code,
    pause,
)
from .client import ClaudeClient, LLMResponse, ToolCall

__all__ = [
    "banner",
    "concept",
    "h1",
    "h2",
    "rule",
    "wrong",
    "right",
    "tip",
    "note",
    "kv",
    "bullet",
    "code",
    "pause",
    "ClaudeClient",
    "LLMResponse",
    "ToolCall",
]
