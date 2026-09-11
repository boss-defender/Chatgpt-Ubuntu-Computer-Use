"""Command-line entry point for the Ubuntu computer-use companion MVP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import ComputerUseAgent
from .runtime import DryRunRuntime, PyAutoGUIRuntime
from .safety import ApprovalManager, AuditLog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe Ubuntu computer-use companion MVP")
    parser.add_argument("--prompt", help="task to send to the model")
    parser.add_argument("--demo", action="store_true", help="run an offline dry-run action demo")
    parser.add_argument("--live", action="store_true", help="enable opt-in PyAutoGUI desktop input")
    parser.add_argument("--auto-approve", action="store_true", help="skip action confirmations")
    parser.add_argument("--model", help="Responses API model (default: gpt-5.6-sol)")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--audit", default="work/audit.jsonl")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audit = AuditLog(Path(args.audit))
    approval = ApprovalManager(auto_approve=args.auto_approve)

    if args.demo:
        # The offline demo is deterministic and must not wait for terminal input.
        runtime = DryRunRuntime(args.width, args.height, ApprovalManager(auto_approve=True), audit)
        result = runtime.execute_actions(
            [
                {"type": "screenshot"},
                {"type": "click", "x": 240, "y": 160, "button": "left"},
                {"type": "type", "text": "Ubuntu companion demo"},
            ]
        )
        print(json.dumps({"mode": "dry-run", "messages": result.messages}, indent=2))
        return 0

    if not args.prompt:
        print("Provide --prompt or use --demo.", file=sys.stderr)
        return 2

    if args.live:
        runtime = PyAutoGUIRuntime(args.width, args.height, approval, audit)
    else:
        runtime = DryRunRuntime(args.width, args.height, approval, audit)
        print("Dry-run mode: proposed actions will be logged, not sent to the desktop.")

    agent = ComputerUseAgent(runtime, model=args.model, max_turns=args.max_turns)
    print(agent.run(args.prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
