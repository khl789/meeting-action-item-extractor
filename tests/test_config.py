import os
import tempfile
import unittest
from pathlib import Path

from meeting_action_extractor.config import load_project_env


class ConfigTests(unittest.TestCase):
    def test_load_project_env_without_overwriting_existing_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / ".env"
            path.write_text("OPENROUTER_API_KEY=file-key\nOPENROUTER_MODEL=test/model\n")
            previous_key = os.environ.get("OPENROUTER_API_KEY")
            previous_model = os.environ.get("OPENROUTER_MODEL")
            try:
                os.environ["OPENROUTER_API_KEY"] = "existing-key"
                os.environ.pop("OPENROUTER_MODEL", None)
                load_project_env(str(path))
                self.assertEqual(os.environ["OPENROUTER_API_KEY"], "existing-key")
                self.assertEqual(os.environ["OPENROUTER_MODEL"], "test/model")
            finally:
                if previous_key is None:
                    os.environ.pop("OPENROUTER_API_KEY", None)
                else:
                    os.environ["OPENROUTER_API_KEY"] = previous_key
                if previous_model is None:
                    os.environ.pop("OPENROUTER_MODEL", None)
                else:
                    os.environ["OPENROUTER_MODEL"] = previous_model


if __name__ == "__main__":
    unittest.main()
