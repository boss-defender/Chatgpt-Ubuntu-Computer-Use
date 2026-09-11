import unittest

from ubuntu_companion.runtime import DryRunRuntime
from ubuntu_companion.safety import ApprovalManager, AuditLog


class RuntimeTests(unittest.TestCase):
    def test_dry_run_keeps_actions_local(self):
        runtime = DryRunRuntime(100, 100, ApprovalManager(auto_approve=True), AuditLog("/tmp/ubuntu-companion-test.jsonl"))
        result = runtime.execute_actions([{"type": "click", "x": 10, "y": 20}])
        self.assertEqual(runtime.executed[0]["type"], "click")
        self.assertIn("dry-run: click", result.messages)
        self.assertGreater(len(result.screenshot), 10)


if __name__ == "__main__":
    unittest.main()

