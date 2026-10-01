"""Check whether action-item evidence and optional fields are supported or abstained."""

from typing import Any, Dict, List

from .models import ActionItem


def validate_evidence(items: List[ActionItem], transcript: str) -> List[Dict[str, Any]]:
    checks = []
    normalized_transcript = " ".join(transcript.split())
    for index, item in enumerate(items):
        normalized_evidence = " ".join(item.evidence.split())
        checks.append(
            {
                "index": index,
                "evidence_supported": normalized_evidence in normalized_transcript,
                "owner_abstained": item.owner is None,
                "due_date_abstained": item.due_date is None,
            }
        )
    return checks
