"""Test conversion of representative AMI XML annotations."""

import tempfile
import unittest
from pathlib import Path

from meeting_action_extractor.ami import export_ami_meeting


MEETINGS = """<?xml version="1.0"?>
<nite:root xmlns:nite="http://nite.sourceforge.net/">
  <meeting observation="TEST001a" type="scenario">
    <speaker nxt_agent="A" role="PM"/>
  </meeting>
</nite:root>"""

WORDS = """<?xml version="1.0"?>
<nite:root xmlns:nite="http://nite.sourceforge.net/">
  <w nite:id="TEST001a.A.words0" starttime="1.0" endtime="1.2">I</w>
  <w nite:id="TEST001a.A.words1" starttime="1.2" endtime="1.4">will</w>
  <w nite:id="TEST001a.A.words2" starttime="1.4" endtime="1.8">send</w>
  <w nite:id="TEST001a.A.words3" starttime="1.8" endtime="1.8" punc="true">.</w>
</nite:root>"""

DIALOGUE = """<?xml version="1.0"?>
<nite:root xmlns:nite="http://nite.sourceforge.net/">
  <dact nite:id="d1">
    <nite:child href="TEST001a.A.words.xml#id(TEST001a.A.words0)..id(TEST001a.A.words3)"/>
  </dact>
</nite:root>"""

SUMMARY = """<?xml version="1.0"?>
<nite:root xmlns:nite="http://nite.sourceforge.net/">
  <actions><sentence>The project manager will send the file.</sentence></actions>
</nite:root>"""


class AmiImportTests(unittest.TestCase):
    def test_export_meeting(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            output = Path(temporary) / "output"
            for directory in ["corpusResources", "words", "dialogueActs", "abstractive"]:
                (source / directory).mkdir(parents=True, exist_ok=True)
            (source / "corpusResources/meetings.xml").write_text(MEETINGS)
            (source / "words/TEST001a.A.words.xml").write_text(WORDS)
            (source / "dialogueActs/TEST001a.A.dialog-act.xml").write_text(DIALOGUE)
            (source / "abstractive/TEST001a.abssumm.xml").write_text(SUMMARY)

            report = export_ami_meeting(str(source), "TEST001a", str(output))
            transcript = (output / "transcript.txt").read_text()
            self.assertEqual(transcript, "A/PM: I will send.\n")
            self.assertEqual(report["reference_action_count"], 1)


if __name__ == "__main__":
    unittest.main()
