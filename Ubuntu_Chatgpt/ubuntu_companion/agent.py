"""OpenAI Responses API loop for structured computer-use actions."""

from __future__ import annotations

import base64
import os
from typing import Any

from .runtime import DesktopRuntime


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


class ComputerUseAgent:
    """Drive a persistent local runtime through the Responses API."""

    def __init__(self, runtime: DesktopRuntime, model: str | None = None, max_turns: int = 20) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:
            raise RuntimeError("API mode requires the optional 'openai' package") from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("API mode requires OPENAI_API_KEY; use --demo to test offline")
        self.client = OpenAI()
        self.runtime = runtime
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")
        self.max_turns = max_turns

    def run(self, prompt: str) -> str:
        next_input: Any = prompt
        previous_response_id = None
        for turn in range(self.max_turns):
            request: dict[str, Any] = {
                "model": self.model,
                "tools": [{"type": "computer"}],
                "input": next_input,
            }
            if previous_response_id:
                request["previous_response_id"] = previous_response_id
            response = self.client.responses.create(**request)
            output = _field(response, "output", []) or []
            calls = [item for item in output if _field(item, "type") == "computer_call"]
            if not calls:
                text = _field(response, "output_text", "")
                return text or "The model completed without a final text response."
            if turn == self.max_turns - 1:
                raise RuntimeError(f"run reached the {self.max_turns}-turn limit")

            next_input = []
            for call in calls:
                actions = [_as_dict(action) for action in (_field(call, "actions", []) or [])]
                result = self.runtime.execute_actions(actions)
                encoded = base64.b64encode(result.screenshot).decode("ascii")
                next_input.append(
                    {
                        "type": "computer_call_output",
                        "call_id": _field(call, "call_id"),
                        "output": {
                            "type": "computer_screenshot",
                            "image_url": f"data:image/png;base64,{encoded}",
                            "detail": "original",
                        },
                    }
                )
            previous_response_id = _field(response, "id")
        raise RuntimeError("computer-use loop ended unexpectedly")


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return {key: getattr(value, key) for key in dir(value) if not key.startswith("_")}

