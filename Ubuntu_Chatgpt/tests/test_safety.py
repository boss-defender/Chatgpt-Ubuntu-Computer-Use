import tempfile
import unittest
from pathlib import Path

from ubuntu_companion.safety import AuditLog, SafetyError, action_requires_approval, validate_action


class SafetyTests(unittest.TestCase):
    def test_valid_click_is_normalized(self):
        self.assertEqual(validate_action({"type": "click", "x": 4.8, "y": 5.2}, 100, 100)["x"], 4)

    def test_out_of_bounds_click_is_rejected(self):
        with self.assertRaises(SafetyError):
            validate_action({"type": "click", "x": 100, "y": 5}, 100, 100)

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(SafetyError):
            validate_action({"type": "shell", "command": "rm -rf /"}, 100, 100)

    def test_sensitive_text_requires_approval_even_in_relaxed_mode(self):
        action = {"type": "type", "text": "enter API key here"}
        self.assertTrue(action_requires_approval(action, approve_every_action=False))

    def test_audit_log_is_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            AuditLog(path).write("proposed", {"type": "screenshot"})
            self.assertIn('"event": "proposed"', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

