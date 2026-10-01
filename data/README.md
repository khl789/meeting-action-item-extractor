# Data documentation

## Dataset

This project uses selected scenario-meeting transcripts from the AMI Meeting Corpus. The repository contains project-specific action-item annotations derived from those meetings. Users who want to reproduce the transcript conversion must obtain the original AMI manual annotation release from the official corpus website and follow its licence and attribution requirements.

The small files under `sample/` are synthetic and exist only for testing and demonstration. They are not included in the reported evaluation results.

## Data split

The evaluation uses whole meetings rather than randomly splitting individual action items. This prevents content from the same meeting appearing in both development and test data.

- `annotations/development/` contains 20 meetings used for annotation refinement, prompt development, and model selection. These meetings contain 49 gold action items.
- `annotations/test/` contains 20 held-out meetings used once for final evaluation. These meetings contain 66 gold action items, so the primary held-out sample size is `n = 66`.
- `splits/meeting-split.json` records the meeting IDs assigned to each split.

The final prompt, model, decoding settings, matching method, and matching threshold were frozen before the held-out results were inspected. No held-out example was used to tune the system.

## Annotation format

Each JSON annotation file contains confirmed future action items. Every item records:

- `action`: the task or deliverable;
- `owner`: the responsible participant, or `null` when unsupported;
- `due_date`: an explicit deadline, or `null` when unsupported; and
- `evidence`: an exact quotation from the meeting transcript.

Only confirmed commitments or assignments are labelled. Tentative suggestions, completed past actions, general discussion, and unsupported guesses are excluded. The complete labelling rules are documented in [`../docs/annotation-guide.md`](../docs/annotation-guide.md).

## Reproducibility and limitations

The action item is the primary evaluation unit. Results should therefore report the number of gold action items as well as the number of meetings. The annotations were produced for this course project by one annotator, so inter-annotator agreement was not measured. The selected AMI scenario meetings may not represent confidential, multilingual, highly technical, or informal workplace meetings.
