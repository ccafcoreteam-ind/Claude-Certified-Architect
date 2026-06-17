"""A small Claude client wrapper for the teaching demos.

Why a wrapper? Two reasons:

1. Classroom-friendly. The demos must run with zero setup. If there is no API key
   (or no network, or the SDK isn't installed) the client falls back to a
   *simulator* the demo supplies. The simulation is clearly labelled so nobody
   mistakes it for a real model response.

2. One honest surface. Real Claude responses and simulated ones are normalised
   into the same `LLMResponse` shape (text, stop_reason, tool_calls). That lets a
   demo show the exact control-flow an Agent SDK loop uses — `stop_reason` checks,
   appending tool results, looping — without branching on "is this real or fake".

The model id used for live calls is the latest generally-available Claude model.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

# The current default model for new builds. Swap via CCARCH_MODEL if needed.
DEFAULT_MODEL = os.environ.get("CCARCH_MODEL", "claude-sonnet-4-6")


@dataclass
class ToolCall:
    """A request from the model to run a tool (Agent SDK / API `tool_use` block)."""

    name: str
    input: dict[str, Any] = field(default_factory=dict)
    id: str = "toolu_demo"


@dataclass
class LLMResponse:
    """Normalised model response shared by live and simulated modes."""

    text: str = ""
    stop_reason: str = "end_turn"  # "end_turn" | "tool_use"
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None
    simulated: bool = False

    @property
    def wants_tool(self) -> bool:
        return self.stop_reason == "tool_use"


# A simulator is any function that, given (system, messages, tools), returns an
# LLMResponse. Demos pass one so they keep working offline.
Simulator = Callable[[str, list[dict], Optional[list[dict]]], LLMResponse]


class ClaudeClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self._api = None
        self.mode = "simulated"
        key = os.environ.get("ANTHROPIC_API_KEY")
        if key:
            try:  # only import the SDK if a key is present
                import anthropic  # type: ignore

                self._api = anthropic.Anthropic(api_key=key)
                self.mode = "live"
            except Exception:  # SDK missing / import error -> stay simulated
                self._api = None
                self.mode = "simulated"

    # ------------------------------------------------------------------ #
    def complete(
        self,
        system: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[dict] = None,
        simulator: Optional[Simulator] = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Return a normalised response, live if possible, else simulated."""
        if self.mode == "live" and self._api is not None:
            try:
                return self._live(system, messages, tools, tool_choice, max_tokens)
            except Exception as exc:  # network/key/rate-limit -> degrade gracefully
                print(f"    [client] live call failed ({exc}); using simulation")
        if simulator is not None:
            resp = simulator(system, messages, tools)
            resp.simulated = True
            return resp
        return LLMResponse(
            text="[no simulator supplied for offline mode]",
            simulated=True,
        )

    # ------------------------------------------------------------------ #
    def _live(self, system, messages, tools, tool_choice, max_tokens) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        msg = self._api.messages.create(**kwargs)
        text_parts, calls = [], []
        for block in msg.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                calls.append(ToolCall(name=block.name, input=block.input, id=block.id))
        return LLMResponse(
            text="\n".join(text_parts),
            stop_reason=msg.stop_reason or "end_turn",
            tool_calls=calls,
            raw=msg,
            simulated=False,
        )


def pretty_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)
