import re
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .models import ActionItem
from .validation import validate_evidence


TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(value: str) -> set:
    return set(TOKEN.findall(value.lower()))


def _jaccard(left_text: str, right_text: str) -> float:
    left_tokens = _tokens(left_text)
    right_tokens = _tokens(right_text)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _similarity(left: ActionItem, right: ActionItem) -> float:
    action_similarity = _jaccard(left.action, right.action)
    combined_similarity = _jaccard(
        left.action + " " + left.evidence,
        right.action + " " + right.evidence,
    )
    return max(action_similarity, combined_similarity)


def match_items(
    gold: Sequence[ActionItem], predictions: Sequence[ActionItem], threshold: float = 0.30
) -> List[Tuple[int, int, float]]:
    candidates = []
    for gi, gold_item in enumerate(gold):
        for pi, predicted_item in enumerate(predictions):
            score = _similarity(gold_item, predicted_item)
            if score >= threshold:
                candidates.append((score, gi, pi))
    candidates.sort(reverse=True)

    matches = []
    used_gold = set()
    used_predictions = set()
    for score, gi, pi in candidates:
        if gi not in used_gold and pi not in used_predictions:
            used_gold.add(gi)
            used_predictions.add(pi)
            matches.append((gi, pi, score))
    return matches


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _slot_accuracy(
    matches: Iterable[Tuple[int, int, float]],
    gold: Sequence[ActionItem],
    predictions: Sequence[ActionItem],
    field: str,
) -> float:
    pairs = list(matches)
    correct = sum(
        getattr(gold[gi], field) == getattr(predictions[pi], field) for gi, pi, _ in pairs
    )
    return _safe_divide(correct, len(pairs))


def evaluate(
    gold: Sequence[ActionItem],
    predictions: Sequence[ActionItem],
    transcript: str,
    threshold: float = 0.30,
) -> Dict[str, Any]:
    matches = match_items(gold, predictions, threshold)
    true_positive = len(matches)
    precision = _safe_divide(true_positive, len(predictions))
    recall = _safe_divide(true_positive, len(gold))
    f1 = _safe_divide(2 * precision * recall, precision + recall)
    checks = validate_evidence(list(predictions), transcript)

    return {
        "counts": {
            "gold": len(gold),
            "predicted": len(predictions),
            "matched": true_positive,
            "false_positive": len(predictions) - true_positive,
            "false_negative": len(gold) - true_positive,
        },
        "detection": {"precision": precision, "recall": recall, "f1": f1},
        "slots_on_matched_items": {
            "owner_accuracy": _slot_accuracy(matches, gold, predictions, "owner"),
            "due_date_accuracy": _slot_accuracy(matches, gold, predictions, "due_date"),
        },
        "safety": {
            "evidence_supported_rate": _safe_divide(
                sum(check["evidence_supported"] for check in checks), len(checks)
            ),
            "owner_abstention_rate": _safe_divide(
                sum(check["owner_abstained"] for check in checks), len(checks)
            ),
            "due_date_abstention_rate": _safe_divide(
                sum(check["due_date_abstained"] for check in checks), len(checks)
            ),
        },
        "matching_threshold": threshold,
        "matches": [
            {"gold_index": gi, "prediction_index": pi, "similarity": score}
            for gi, pi, score in matches
        ],
    }
