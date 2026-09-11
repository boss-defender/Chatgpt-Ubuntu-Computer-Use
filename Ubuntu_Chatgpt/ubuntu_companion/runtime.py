"""Desktop runtimes: deterministic dry-run and optional PyAutoGUI live control."""

from __future__ import annotations

import base64
import io
import time
from dataclasses import dataclass
from typing import Any

from .safety import (
    ApprovalManager,
    AuditLog,
    SafetyError,
    action_requires_approval,
    validate_action,
)


# A valid 1x1 PNG used as an observation in dry-run mode.
DRY_RUN_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


@dataclass
class ActionResult:
    """The local observation returned after a batch of actions."""

    messages: list[str]
    screenshot: bytes


class DesktopRuntime:
    """Interface consumed by the OpenAI response loop."""

    width: int
    height: int

    def capture(self) -> bytes:
        raise NotImplementedError

    def execute_actions(self, actions: list[dict[str, Any]]) -> ActionResult:
        raise NotImplementedError


class SafeRuntimeMixin:
    def __init__(
        self,
        width: int,
        height: int,
        approval: ApprovalManager,
        audit: AuditLog,
        approve_every_action: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.approval = approval
        self.audit = audit
        self.approve_every_action = approve_every_action

    def _validated_actions(self, actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        validated = []
        for action in actions:
            try:
                checked = validate_action(action, self.width, self.height)
            except SafetyError as exc:
                self.audit.write("rejected", action, reason=str(exc))
                raise
            self.audit.write("proposed", checked)
            if action_requires_approval(checked, self.approve_every_action):
                if not self.approval.approve(checked):
                    self.audit.write("denied", checked)
                    continue
                self.audit.write("approved", checked)
            validated.append(checked)
        return validated


class DryRunRuntime(SafeRuntimeMixin, DesktopRuntime):
    """No-op runtime that records and displays what would happen."""

    def __init__(
        self,
        width: int = 1440,
        height: int = 900,
        approval: ApprovalManager | None = None,
        audit: AuditLog | None = None,
        approve_every_action: bool = True,
    ) -> None:
        super().__init__(
            width,
            height,
            approval or ApprovalManager(auto_approve=True),
            audit or AuditLog("work/audit.jsonl"),
            approve_every_action,
        )
        self.executed: list[dict[str, Any]] = []

    def capture(self) -> bytes:
        return DRY_RUN_PNG

    def execute_actions(self, actions: list[dict[str, Any]]) -> ActionResult:
        checked = self._validated_actions(actions)
        self.executed.extend(checked)
        messages = [f"dry-run: {action['type']}" for action in checked]
        return ActionResult(messages or ["no action executed"], self.capture())


class PyAutoGUIRuntime(SafeRuntimeMixin, DesktopRuntime):
    """Opt-in live runtime for a local desktop session."""

    def __init__(
        self,
        width: int,
        height: int,
        approval: ApprovalManager,
        audit: AuditLog,
        approve_every_action: bool = True,
    ) -> None:
        try:
            import pyautogui  # type: ignore
        except ImportError as exc:
            raise RuntimeError("live mode requires the optional 'pyautogui' package") from exc
        super().__init__(width, height, approval, audit, approve_every_action)
        self.pyautogui = pyautogui
        self.pyautogui.PAUSE = 0.12
        self.pyautogui.FAILSAFE = True

    def capture(self) -> bytes:
        image = self.pyautogui.screenshot()
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def execute_actions(self, actions: list[dict[str, Any]]) -> ActionResult:
        checked = self._validated_actions(actions)
        messages = []
        for action in checked:
            kind = action["type"]
            if kind == "click":
                self.pyautogui.click(action["x"], action["y"], button=action.get("button", "left"))
            elif kind == "double_click":
                self.pyautogui.doubleClick(action["x"], action["y"], button=action.get("button", "left"))
            elif kind == "move":
                self.pyautogui.moveTo(action["x"], action["y"])
            elif kind == "drag":
                path = action["path"]
                self.pyautogui.moveTo(path[0]["x"], path[0]["y"])
                self.pyautogui.mouseDown()
                for point in path[1:]:
                    self.pyautogui.moveTo(point["x"], point["y"], duration=0.05)
                self.pyautogui.mouseUp()
            elif kind == "scroll":
                self.pyautogui.scroll(action["scroll_y"])
            elif kind == "keypress":
                self.pyautogui.press(action["keys"])
            elif kind == "type":
                self.pyautogui.write(action["text"], interval=0.01)
            elif kind == "wait":
                time.sleep(action["seconds"])
            elif kind == "screenshot":
                pass
            messages.append(f"executed: {kind}")
            self.audit.write("executed", action)
        return ActionResult(messages or ["no action executed"], self.capture())

