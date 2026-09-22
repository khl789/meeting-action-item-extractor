from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ActionItem:
    action: str
    owner: Optional[str]
    due_date: Optional[str]
    evidence: str
    confidence: Optional[float] = None

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "ActionItem":
        action = value.get("action")
        evidence = value.get("evidence")
        if not isinstance(action, str) or not action.strip():
            raise ValueError("action must be a non-empty string")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError("evidence must be a non-empty string")

        owner = value.get("owner")
        due_date = value.get("due_date")
        confidence = value.get("confidence")
        if owner is not None and not isinstance(owner, str):
            raise ValueError("owner must be a string or null")
        if due_date is not None and not isinstance(due_date, str):
            raise ValueError("due_date must be a string or null")
        if confidence is not None:
            confidence = float(confidence)
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("confidence must be between 0 and 1")

        return cls(
            action=action.strip(),
            owner=owner.strip() if owner else None,
            due_date=due_date.strip() if due_date else None,
            evidence=evidence.strip(),
            confidence=confidence,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def parse_action_items(payload: Dict[str, Any]) -> List[ActionItem]:
    values = payload.get("action_items")
    if not isinstance(values, list):
        raise ValueError("payload must contain an action_items list")
    return [ActionItem.from_dict(item) for item in values]
