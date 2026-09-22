import json
import unittest
from pathlib import Path

from meeting_action_extractor.evaluation import evaluate, match_items
from meeting_action_extractor.models import parse_action_items
from meeting_action_extractor.rules import extract_with_rules
from meeting_action_extractor.validation import validate_evidence


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.transcript = (ROOT / "data/sample/transcript.txt").read_text(encoding="utf-8")
        payload = json.loads((ROOT / "data/sample/gold.json").read_text(encoding="utf-8"))
        self.gold = parse_action_items(payload)

    def test_rules_extract_confirmed_items_and_skip_tentative(self):
        items = extract_with_rules(self.transcript)
        evidence = [item.evidence for item in items]
        self.assertIn("Daniel: I'll send the revised checklist by Friday.", evidence)
        self.assertNotIn("Daniel: Maybe we should redesign the invitation later.", evidence)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[1].due_date, "tomorrow")

    def test_all_rule_evidence_is_present(self):
        items = extract_with_rules(self.transcript)
        checks = validate_evidence(items, self.transcript)
        self.assertTrue(all(check["evidence_supported"] for check in checks))

    def test_evaluation_is_bounded(self):
        report = evaluate(self.gold, extract_with_rules(self.transcript), self.transcript)
        self.assertGreaterEqual(report["detection"]["f1"], 0.0)
        self.assertLessEqual(report["detection"]["f1"], 1.0)

    def test_gold_schema_round_trip(self):
        self.assertEqual(self.gold[0].owner, "Daniel")
        self.assertIsNone(self.gold[0].confidence)

    def test_matching_can_use_action_text_when_evidence_lines_differ(self):
        gold = parse_action_items({"action_items": [{
            "action": "work on trend watching",
            "owner": "D/ME",
            "due_date": None,
            "evidence": "PM: marketing will work on trend watching.",
            "confidence": None,
        }]})
        prediction = parse_action_items({"action_items": [{
            "action": "think about trend watching",
            "owner": "D/ME",
            "due_date": None,
            "evidence": "PM: there will be thirty minutes of work.",
            "confidence": None,
        }]})
        self.assertEqual(len(match_items(gold, prediction)), 1)


if __name__ == "__main__":
    unittest.main()
