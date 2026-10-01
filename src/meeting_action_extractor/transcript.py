"""Parse speaker-labelled text transcripts into ordered utterance records."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Utterance:
    speaker: str
    text: str
    raw: str


SPEAKER_LINE = re.compile(r"^\s*([^:\n]{1,80}):\s*(.+?)\s*$")


def parse_transcript(text: str) -> List[Utterance]:
    utterances = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = SPEAKER_LINE.match(line)
        if match:
            utterances.append(
                Utterance(
                    speaker=match.group(1).strip(),
                    text=match.group(2).strip(),
                    raw=line.strip(),
                )
            )
        else:
            utterances.append(Utterance(speaker="Unknown", text=line.strip(), raw=line.strip()))
    return utterances


def read_transcript(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
