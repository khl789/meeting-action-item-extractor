# Meeting Action-Item Extractor

This PE6201 project builds and evaluates a transparent system that extracts confirmed action items from existing workplace meeting transcripts. Each output contains an action, owner, due date, and supporting evidence. Missing fields are returned as `null` rather than guessed.

## Scope

The project accepts text transcripts as input. It does not record meetings, perform speech-to-text, summarize meetings, schedule tasks, or act autonomously. A project manager reviews every extracted item before using it.

## Research question

Can a hosted foundation model extract confirmed meeting action items more accurately than a reproducible rule-based baseline while keeping unsupported owner and due-date predictions low?

## System design

1. Parse speaker-labelled transcript lines.
2. Run either a deterministic rule baseline or a hosted model through OpenRouter.
3. Validate the output schema and verify that every evidence quote occurs in the source transcript.
4. Compare predictions with frozen human labels.
5. Report detection F1, slot accuracy, unsupported evidence rate, abstention, latency, and estimated API cost.

## Quick start

The baseline and tests require only Python 3.9 or newer.

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m meeting_action_extractor extract \
  --method rules \
  --input data/sample/transcript.txt \
  --output outputs/rules.json
PYTHONPATH=src python -m meeting_action_extractor evaluate \
  --gold data/sample/gold.json \
  --predictions outputs/rules.json \
  --transcript data/sample/transcript.txt
```

For OpenRouter, save credentials with hidden input rather than committing them:

```bash
PYTHONPATH=src python -m meeting_action_extractor configure
PYTHONPATH=src python -m meeting_action_extractor check-config
PYTHONPATH=src python -m meeting_action_extractor extract \
  --method openrouter \
  --input data/sample/transcript.txt \
  --output outputs/model.json
```

The configuration command uses `openai/gpt-5.6-luna` by default and writes the key to a permission-restricted `.env` file excluded by `.gitignore`. The program never prints the key.

Choose and record a fixed model identifier before the final evaluation. Do not change the prompt, model, labels, or matching threshold after inspecting held-out results.

### Evaluation rule

The primary evaluation unit is the action item, not the meeting transcript. The held-out test split contains 20 meetings and 66 gold action items, so the primary test sample size is `n = 66`.

Detection uses a frozen one-to-one matcher. Text is lowercased and reduced to unique alphanumeric tokens. For every gold/prediction pair, the matcher calculates token-set Jaccard similarity for (1) the action text and (2) the combined action-and-evidence text, then keeps the higher score. Candidate pairs scoring at least 0.30 are greedily matched from highest to lowest score, with each gold and predicted item used at most once. Owner and due-date values do not determine a detection match; they are scored separately on matched items so that an owner error is not counted twice.

## Data protocol

- Use AMI scenario-meeting transcripts under their applicable licence.
- Keep whole meetings in only one split to avoid leakage.
- Write the annotation guide before final evaluation.
- Freeze held-out labels before running either evaluated method.
- Label only confirmed commitments or assignments.
- Use `null` when an owner or deadline is not supported by the text.
- Preserve an exact supporting quote for auditability.

The included sample is synthetic and exists only to test the pipeline. It is not evaluation evidence.

## Import AMI annotations

Download and unpack the AMI manual annotation release, then convert a meeting:

```bash
PYTHONPATH=src python -m meeting_action_extractor import-ami \
  --source data/raw/ami/manual \
  --meeting ES2002a \
  --output-dir data/processed/ES2002a
```

The converter joins word-level XML using AMI dialogue-act boundaries, orders all speakers by time, and maps channel letters to scenario roles. The generated `metadata.json` includes AMI's abstractive `ACTIONS` sentences as annotation aids. They are not accepted as gold labels because they do not contain exact transcript evidence and may follow a different task definition.

For development labels, keep manually verified JSON under `data/annotations/development/`. Keep final held-out labels under `data/annotations/test/` and do not inspect model results on those meetings until the experiment is frozen.

## Repository structure

```text
data/sample/          Synthetic smoke-test transcript and gold labels
docs/                 Annotation and experiment protocols
src/                  Extractors, validation, evaluation, and CLI
tests/                Automated tests
outputs/              Generated predictions, excluded from version control
```

## Reproducibility

Record the Python version, model identifier, prompt version, decoding parameters, dataset meeting IDs, split file, timestamp, latency, and token usage for every final experiment. Keep the OpenRouter key outside the repository.

## Final results

The final v13 system was selected using only the development set and was evaluated once on 20 held-out test meetings containing 66 gold action items (`n = 66` for the primary action-item evaluation).

| Method | Precision | Recall | F1 | Owner accuracy | Due-date accuracy | Evidence support |
|---|---:|---:|---:|---:|---:|---:|
| v13 LLM extractor | 0.732 | 0.621 | 0.672 | 0.537 | 0.707 | 0.893 |
| Rule baseline | 0.031 | 0.227 | 0.055 | 0.533 | 0.667 | 1.000 |

The v13 system processed the 20 test meetings for USD 0.07739 in total, with an average latency of 10.77 seconds per meeting. Full experimental results and error analysis are available in [`docs/final-results.md`](docs/final-results.md).

## Short demonstration

The repository includes a synthetic meeting transcript containing two confirmed commitments, one tentative suggestion, and one statement about a past event.

Run the frozen v13 extractor:

```bash
PYTHONPATH=src python3 -m meeting_action_extractor extract \
  --method openrouter \
  --input data/sample/transcript.txt \
  --output outputs/demo-v13.json
```

Display the extracted action items:

```bash
jq -r '.action_items[] | "TASK: \(.action)\nOWNER: \(.owner // "Not specified")\nDUE: \(.due_date // "Not specified")\nEVIDENCE: \(.evidence)\n"' outputs/demo-v13.json
```

The expected output contains two action items:

1. Daniel sends the revised checklist by Friday.
2. Priya confirms the venue tomorrow.

The tentative invitation redesign and the previously approved budget are correctly excluded.

### Browser demonstration

Start the local review interface and open it in a browser:

```bash
PYTHONPATH=src python3 -m meeting_action_extractor serve --open-browser
```

The interface runs only on `127.0.0.1`, keeps the OpenRouter key on the local computer, and shows each
extracted action together with its owner, due date, confidence, and exact supporting quotation. Select
`Rule baseline` in the interface to demonstrate the reproducible comparison method.

## Data attribution

This project uses transcripts and manual annotations from the [AMI Meeting Corpus](https://groups.inf.ed.ac.uk/ami/corpus/), created by the AMI Consortium. The AMI manual annotations, including orthographic transcripts, are distributed under the [Creative Commons Attribution 4.0 International licence](https://groups.inf.ed.ac.uk/ami/download/).

The repository contains project-specific action-item labels derived from selected AMI scenario meetings. Large original downloads and processed transcripts are excluded from version control. Users must obtain the source corpus from the official AMI site and comply with its attribution requirements.
