"""Test the frozen hosted-model prompt and its task-definition safeguards."""

import unittest

from meeting_action_extractor.openrouter import PROMPT_VERSION, SYSTEM_PROMPT


class OpenRouterPromptTests(unittest.TestCase):
    def test_v13_prompt_supports_reviewed_task_rules(self) -> None:
        self.assertEqual(PROMPT_VERSION, "v13")
        self.assertIn("any participant as their own substantive project task", SYSTEM_PROMPT)
        self.assertIn("self-stated routine meeting-administration actions", SYSTEM_PROMPT)
        self.assertIn("product requirement or design decision", SYSTEM_PROMPT)
        self.assertIn("later in the current", SYSTEM_PROMPT)
        self.assertIn("performed immediately in the current meeting", SYSTEM_PROMPT)
        self.assertIn("open-ended or recurring promises", SYSTEM_PROMPT)
        self.assertIn("join all confirmed speaker labels", SYSTEM_PROMPT)
        self.assertIn("immediately adjacent assignment exchange", SYSTEM_PROMPT)
        self.assertIn("explicit collective commitment", SYSTEM_PROMPT)
        self.assertIn("every distinct qualifying assignment", SYSTEM_PROMPT)
        self.assertIn("keep that list together as one action item", SYSTEM_PROMPT)
        self.assertIn("concrete one-time conditional deliverable", SYSTEM_PROMPT)
        self.assertIn("exactly one complete transcript line verbatim", SYSTEM_PROMPT)
        self.assertIn("Never join multiple lines", SYSTEM_PROMPT)
        self.assertIn("Preserve every filler", SYSTEM_PROMPT)
        self.assertIn("Do not treat a work period", SYSTEM_PROMPT)
        self.assertIn('never output "before the next meeting"', SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
