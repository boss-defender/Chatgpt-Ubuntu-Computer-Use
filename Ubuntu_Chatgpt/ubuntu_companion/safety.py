"""Action validation, approval, and audit logging for desktop control."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ALLOWED_ACTIONS = {
    "click",
    "double_click",
    "drag",
    "move",
    "scroll",
    "keypress",
    "type",
    "wait",
    "screenshot",
}

SENSITIVE_PATTERNS = (
    re.compile(r"\b(password|passcode|pin|secret|token|api[ _-]?key)\b", re.I),
    re.compile(r"\b(card|credit|debit)\b", re.I),
)


class SafetyError(ValueError):
    """Raised when a model-proposed action is outside the local policy."""


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SafetyError(f"{label} must be a number")
    return float(value)


def validate_action(action: dict[str, Any], width: int, height: int) -> dict[str, Any]:
    """Validate and normalize one computer-tool action."""

    if not isinstance(action, dict):
        raise SafetyError("action must be an object")
    action_type = action.get("type")
    if action_type not in ALLOWED_ACTIONS:
        raise SafetyError(f"unsupported action type: {action_type!r}")

    normalized = dict(action)
    if action_type in {"click", "double_click", "move"}:
        x = _number(action.get("x"), "x")
        y = _number(action.get("y"), "y")
        if not (0 <= x < width and 0 <= y < height):
            raise SafetyError(f"coordinates ({x:g}, {y:g}) outside {width}x{height} screen")
        normalized["x"], normalized["y"] = int(x), int(y)
    elif action_type == "drag":
        path = action.get("path")
        if not isinstance(path, list) or not path or len(path) > 200:
            raise SafetyError("drag path must contain 1-200 points")
        normalized_path = []
        for point in path:
            if not isinstance(point, dict):
                raise SafetyError("drag path points must be objects")
            x = _number(point.get("x"), "drag x")
            y = _number(point.get("y"), "drag y")
            if not (0 <= x < width and 0 <= y < height):
                raise SafetyError(f"drag coordinate ({x:g}, {y:g}) outside screen")
            normalized_path.append({"x": int(x), "y": int(y)})
        normalized["path"] = normalized_path
    elif action_type == "scroll":
        delta = _number(action.get("scroll_y", action.get("delta_y", 0)), "scroll_y")
        if abs(delta) > 5000:
            raise SafetyError("scroll amount is too large")
        normalized["scroll_y"] = int(delta)
    elif action_type == "keypress":
        keys = action.get("keys")
        if not isinstance(keys, list) or not keys or len(keys) > 20:
            raise SafetyError("keypress keys must contain 1-20 keys")
        if any(not isinstance(key, str) or not key or len(key) > 40 for key in keys):
            raise SafetyError("keypress contains an invalid key")
        normalized["keys"] = keys
    elif action_type == "type":
        text = action.get("text")
        if not isinstance(text, str) or len(text) > 5000:
            raise SafetyError("typed text must be a string of at most 5000 characters")
        normalized["text"] = text
    elif action_type == "wait":
        seconds = _number(action.get("seconds", 1), "seconds")
        if not (0 <= seconds <= 30):
            raise SafetyError("wait must be between 0 and 30 seconds")
        normalized["seconds"] = seconds
    return normalized


def action_requires_approval(action: dict[str, Any], approve_every_action: bool = True) -> bool:
    """Return whether a proposed action needs a human confirmation."""

    if action.get("type") in {"screenshot", "wait", "move"}:
        return False
    if approve_every_action:
        return True
    if action.get("type") == "type":
        text = action.get("text", "")
        return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)
    return False


@dataclass
class ApprovalManager:
    """Human-in-the-loop approval callback."""

    auto_approve: bool = False
    prompt: Callable[[str], str] = input

    def approve(self, action: dict[str, Any]) -> bool:
        if self.auto_approve:
            return True
        description = json.dumps(action, sort_keys=True)
        answer = self.prompt(f"Approve desktop action {description}? [y/N] ")
        return answer.strip().lower() in {"y", "yes"}


class AuditLog:
    """Append-only JSONL log of proposed, approved, denied, and rejected actions."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: str, action: dict[str, Any], **extra: Any) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "action": action,
            **extra,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

