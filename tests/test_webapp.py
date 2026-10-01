"""Test browser-demo assets and extraction request handling."""

import unittest

from meeting_action_extractor.webapp import STATIC_DIR, extract_payload


SAMPLE = """Maya: We need to finalize the launch checklist.
Daniel: I'll send the revised checklist by Friday.
Maya: Priya, could you confirm the venue tomorrow?
Priya: Yes, I will confirm it tomorrow.
Daniel: Maybe we should redesign the invitation later.
Maya: The budget was approved yesterday."""


class WebDemoTests(unittest.TestCase):
    def test_static_assets_exist(self):
        for name in ("index.html", "styles.css", "app.js"):
            self.assertTrue((STATIC_DIR / name).is_file())

    def test_rule_demo_returns_supported_items(self):
        payload = extract_payload(SAMPLE, "rules")
        self.assertEqual(len(payload["action_items"]), 2)
        self.assertTrue(all(check["evidence_supported"] for check in payload["validation"]))

    def test_empty_transcript_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_payload("  ", "rules")


if __name__ == "__main__":
    unittest.main()
