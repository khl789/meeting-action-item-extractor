"""Convert AMI XML annotations into ordered, speaker-labelled transcripts."""

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


NITE = "{http://nite.sourceforge.net/}"
WORD_ID = re.compile(r"\.words(\d+)")


@dataclass(frozen=True)
class AmiWord:
    index: int
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class AmiTurn:
    speaker: str
    role: Optional[str]
    start: float
    end: float
    text: str

    def transcript_line(self) -> str:
        label = f"{self.speaker}/{self.role}" if self.role else self.speaker
        return f"{label}: {self.text}"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _join_tokens(tokens: Iterable[str]) -> str:
    text = ""
    punctuation = {".", ",", "?", "!", ";", ":", "'s", "n't"}
    for token in tokens:
        if not token:
            continue
        if not text:
            text = token
        elif token in punctuation or token.startswith("'"):
            text += token
        else:
            text += " " + token
    return " ".join(text.split())


def _word_index(value: str) -> int:
    match = WORD_ID.search(value)
    if not match:
        raise ValueError(f"Cannot read AMI word index from {value!r}")
    return int(match.group(1))


def _load_words(path: Path) -> Dict[int, AmiWord]:
    root = ET.parse(path).getroot()
    words = {}
    for element in root:
        if _local_name(element.tag) not in {"w", "transformerror"}:
            continue
        identifier = element.attrib.get(NITE + "id", "")
        index = _word_index(identifier)
        token = (element.text or element.attrib.get("w", "")).strip()
        words[index] = AmiWord(
            index=index,
            text=token,
            start=float(element.attrib.get("starttime", 0.0)),
            end=float(element.attrib.get("endtime", element.attrib.get("starttime", 0.0))),
        )
    return words


def _load_roles(meetings_path: Path, meeting_id: str) -> Dict[str, str]:
    root = ET.parse(meetings_path).getroot()
    for meeting in root:
        if meeting.attrib.get("observation") == meeting_id:
            return {
                speaker.attrib["nxt_agent"]: speaker.attrib.get("role", "")
                for speaker in meeting
                if _local_name(speaker.tag) == "speaker"
            }
    raise ValueError(f"Meeting {meeting_id} is not present in meetings.xml")


def _href_indices(href: str) -> Tuple[int, int]:
    ids = WORD_ID.findall(href)
    if not ids:
        raise ValueError(f"Cannot read word range from {href!r}")
    return int(ids[0]), int(ids[-1])


def _load_speaker_turns(
    dialogue_path: Path,
    words: Dict[int, AmiWord],
    speaker: str,
    role: Optional[str],
) -> List[AmiTurn]:
    root = ET.parse(dialogue_path).getroot()
    turns = []
    for dact in root:
        indices = []
        for child in dact:
            if _local_name(child.tag) != "child":
                continue
            start_index, end_index = _href_indices(child.attrib.get("href", ""))
            indices.extend(range(start_index, end_index + 1))
        selected = [words[index] for index in indices if index in words]
        text = _join_tokens(word.text for word in selected)
        if selected and text:
            turns.append(
                AmiTurn(
                    speaker=speaker,
                    role=role,
                    start=min(word.start for word in selected),
                    end=max(word.end for word in selected),
                    text=text,
                )
            )
    return turns


def _merge_fragmented_turns(turns: List[AmiTurn], max_gap: float = 2.0) -> List[AmiTurn]:
    """Join adjacent dialogue acts that are visibly one unfinished speaker turn."""
    merged = []
    for turn in turns:
        if (
            merged
            and merged[-1].speaker == turn.speaker
            and turn.start - merged[-1].end <= max_gap
            and not re.search(r"[.?!]$", merged[-1].text)
        ):
            previous = merged[-1]
            merged[-1] = AmiTurn(
                speaker=previous.speaker,
                role=previous.role,
                start=previous.start,
                end=max(previous.end, turn.end),
                text=_join_tokens([previous.text, turn.text]),
            )
        else:
            merged.append(turn)
    return merged


def load_ami_meeting(source_dir: str, meeting_id: str) -> List[AmiTurn]:
    source = Path(source_dir)
    roles = _load_roles(source / "corpusResources/meetings.xml", meeting_id)
    turns = []
    word_paths = sorted((source / "words").glob(f"{meeting_id}.*.words.xml"))
    if not word_paths:
        raise FileNotFoundError(f"No word files found for {meeting_id}")

    for word_path in word_paths:
        speaker = word_path.name.split(".")[1]
        dialogue_path = source / "dialogueActs" / f"{meeting_id}.{speaker}.dialog-act.xml"
        if not dialogue_path.exists():
            raise FileNotFoundError(f"Missing dialogue acts: {dialogue_path}")
        words = _load_words(word_path)
        turns.extend(_load_speaker_turns(dialogue_path, words, speaker, roles.get(speaker)))
    ordered = sorted(turns, key=lambda turn: (turn.start, turn.end, turn.speaker))
    return _merge_fragmented_turns(ordered)


def load_reference_actions(source_dir: str, meeting_id: str) -> List[str]:
    path = Path(source_dir) / "abstractive" / f"{meeting_id}.abssumm.xml"
    if not path.exists():
        return []
    root = ET.parse(path).getroot()
    for section in root:
        if _local_name(section.tag) == "actions":
            return [
                " ".join("".join(sentence.itertext()).split())
                for sentence in section
                if _local_name(sentence.tag) == "sentence"
            ]
    return []


def export_ami_meeting(source_dir: str, meeting_id: str, output_dir: str) -> Dict[str, object]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    turns = load_ami_meeting(source_dir, meeting_id)
    transcript = "\n".join(turn.transcript_line() for turn in turns) + "\n"
    transcript_path = destination / "transcript.txt"
    transcript_path.write_text(transcript, encoding="utf-8")

    metadata = {
        "meeting_id": meeting_id,
        "turn_count": len(turns),
        "duration_seconds": max((turn.end for turn in turns), default=0.0),
        "reference_actions": load_reference_actions(source_dir, meeting_id),
        "reference_actions_warning": (
            "AMI abstractive ACTIONS are annotation aids only. Manually verify every gold item "
            "against the transcript and add exact evidence."
        ),
        "turns": [
            {
                "speaker": turn.speaker,
                "role": turn.role,
                "start": turn.start,
                "end": turn.end,
                "text": turn.text,
            }
            for turn in turns
        ],
    }
    metadata_path = destination / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return {
        "meeting_id": meeting_id,
        "transcript": str(transcript_path),
        "metadata": str(metadata_path),
        "turn_count": len(turns),
        "reference_action_count": len(metadata["reference_actions"]),
    }
