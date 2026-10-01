"""Define commands for extraction, evaluation, configuration, import, and demo serving."""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from .ami import export_ami_meeting
from .config import DEFAULT_MODEL, configure_openrouter, load_project_env
from .evaluation import evaluate
from .models import ActionItem, parse_action_items
from .openrouter import extract_with_openrouter
from .rules import extract_with_rules
from .transcript import read_transcript
from .validation import validate_evidence


def _read_items(path: str) -> List[ActionItem]:
    return parse_action_items(json.loads(Path(path).read_text(encoding="utf-8")))


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_extract(args: argparse.Namespace) -> None:
    transcript = read_transcript(args.input)
    if args.method == "rules":
        items = extract_with_rules(transcript)
        metadata = {"method": "rules", "version": "v1"}
    else:
        items, metadata = extract_with_openrouter(transcript, model=args.model)

    checks = validate_evidence(items, transcript)
    payload = {
        "metadata": metadata,
        "action_items": [item.to_dict() for item in items],
        "validation": checks,
    }
    _write_json(args.output, payload)
    print(f"Wrote {len(items)} action items to {args.output}")


def run_evaluate(args: argparse.Namespace) -> None:
    gold = _read_items(args.gold)
    predictions = _read_items(args.predictions)
    transcript = read_transcript(args.transcript)
    report = evaluate(gold, predictions, transcript, threshold=args.threshold)
    if args.output:
        _write_json(args.output, report)
    print(json.dumps(report, indent=2))


def run_import_ami(args: argparse.Namespace) -> None:
    report = export_ami_meeting(args.source, args.meeting, args.output_dir)
    print(json.dumps(report, indent=2))


def run_configure(args: argparse.Namespace) -> None:
    destination = Path(args.path)
    if destination.exists() and not args.overwrite:
        raise RuntimeError(f"{destination} already exists; use --overwrite to replace it")
    saved = configure_openrouter(args.path, args.model)
    print(f"Saved the key securely in {saved}. This file is excluded from Git.")


def run_check_config(args: argparse.Namespace) -> None:
    load_project_env(args.path)
    key = os.environ.get("OPENROUTER_API_KEY", "")
    model = os.environ.get("OPENROUTER_MODEL", "")
    if not key:
        raise RuntimeError("OpenRouter key is not configured")
    if not model:
        raise RuntimeError("OpenRouter model is not configured")
    print(f"Configuration found. Model: {model}. Key: hidden.")


def run_serve(args: argparse.Namespace) -> None:
    from .webapp import serve

    serve(host=args.host, port=args.port, open_browser=args.open_browser)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract and evaluate meeting action items")
    commands = parser.add_subparsers(dest="command", required=True)

    extract = commands.add_parser("extract", help="extract action items")
    extract.add_argument("--method", choices=["rules", "openrouter"], required=True)
    extract.add_argument("--input", required=True)
    extract.add_argument("--output", required=True)
    extract.add_argument("--model", default="")
    extract.set_defaults(handler=run_extract)

    evaluation = commands.add_parser("evaluate", help="compare predictions with gold labels")
    evaluation.add_argument("--gold", required=True)
    evaluation.add_argument("--predictions", required=True)
    evaluation.add_argument("--transcript", required=True)
    evaluation.add_argument("--threshold", type=float, default=0.30)
    evaluation.add_argument("--output")
    evaluation.set_defaults(handler=run_evaluate)

    import_ami = commands.add_parser("import-ami", help="convert one AMI NXT meeting")
    import_ami.add_argument("--source", required=True, help="unpacked AMI manual annotation directory")
    import_ami.add_argument("--meeting", required=True, help="meeting ID such as ES2002a")
    import_ami.add_argument("--output-dir", required=True)
    import_ami.set_defaults(handler=run_import_ami)

    configure = commands.add_parser("configure", help="securely save OpenRouter settings")
    configure.add_argument("--path", default=".env")
    configure.add_argument("--model", default=DEFAULT_MODEL)
    configure.add_argument("--overwrite", action="store_true")
    configure.set_defaults(handler=run_configure)

    check_config = commands.add_parser("check-config", help="check OpenRouter settings without showing the key")
    check_config.add_argument("--path", default=".env")
    check_config.set_defaults(handler=run_check_config)

    web = commands.add_parser("serve", help="start the local browser demonstration")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8000)
    web.add_argument("--open-browser", action="store_true")
    web.set_defaults(handler=run_serve)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)
