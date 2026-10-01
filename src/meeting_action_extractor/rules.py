"""Provide the deterministic rule-based extractor used as the comparison baseline."""

import re
from dataclasses import replace
from typing import List, Optional

from .models import ActionItem
from .transcript import parse_transcript


SELF_COMMITMENT = re.compile(
    r"\b(?:i will|i'll|i can|let me)\s+(?P<action>.+)", re.IGNORECASE
)
ASSIGNMENT = re.compile(
    r"\b(?P<owner>[A-Z][A-Za-z'-]+),?\s+(?:can|could|will|please|needs? to|should)\s+(?:you\s+)?(?P<action>.+)",
    re.IGNORECASE,
)
DIRECT_REQUEST = re.compile(
    r"\b(?:can|could|will)\s+you\s+(?P<action>.+)", re.IGNORECASE
)
DUE_DATE = re.compile(
    r"\b(?:(?:by|before|due)\s+)?((?:next\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)|tomorrow|today|(?:\d{1,2}[/-]){1,2}\d{2,4}|\d{4}-\d{2}-\d{2})\b",
    re.IGNORECASE,
)
TENTATIVE = re.compile(r"\b(?:maybe|might|perhaps|possibly|if we|could potentially)\b", re.IGNORECASE)


def _clean_action(action: str) -> str:
    action = DUE_DATE.sub("", action)
    return action.strip(" .,:;-?")


def _due_date(text: str) -> Optional[str]:
    match = DUE_DATE.search(text)
    return match.group(1).strip() if match else None


def extract_with_rules(transcript: str) -> List[ActionItem]:
    results = []
    for utterance in parse_transcript(transcript):
        text = utterance.text
        if TENTATIVE.search(text):
            continue

        owner = None
        action = None
        match = SELF_COMMITMENT.search(text)
        if match:
            owner = utterance.speaker if utterance.speaker != "Unknown" else None
            action = match.group("action")

            # Treat an immediate "Yes, I will ..." from the assignee as
            # confirmation of the preceding assignment rather than a new item.
            if (
                re.match(r"^\s*yes\b", text, re.IGNORECASE)
                and results
                and results[-1].owner == owner
            ):
                if results[-1].due_date is None and _due_date(text):
                    results[-1] = replace(results[-1], due_date=_due_date(text))
                continue
        else:
            match = ASSIGNMENT.search(text)
            if match:
                owner = match.group("owner")
                action = match.group("action")
                if owner.lower() in {"i", "we", "you", "he", "she", "they", "it"}:
                    owner = None
                    action = None
            else:
                match = DIRECT_REQUEST.search(text)
                if match:
                    action = match.group("action")

        if action:
            results.append(
                ActionItem(
                    action=_clean_action(action),
                    owner=owner,
                    due_date=_due_date(text),
                    evidence=utterance.raw,
                    confidence=None,
                )
            )
    return results
