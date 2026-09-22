# Experiment Plan

## Compared methods

1. Deterministic rule-based extractor, version v1.
2. One fixed hosted foundation model (`openai/gpt-5.6-luna`), prompt version v2, temperature 0.

## Data split

Select 40 AMI scenario-meeting transcripts. Use 20 meetings for development and 20 held out for final evaluation. Keep all four `a`-`d` meetings from the same scenario series in one split to reduce cross-meeting leakage. Record all IDs in `data/splits/meeting-split.json` before held-out evaluation. The meeting count describes the split, but the primary evaluation unit is the action item. The frozen held-out labels contain 66 gold action items, so the primary test sample size is `n = 66`.

## Primary metric

Action-item detection F1. Text is lowercased and reduced to unique alphanumeric tokens. For each gold/prediction pair, the frozen matcher takes the maximum of two token-set Jaccard similarities: action text alone, and action plus evidence. Candidate pairs at or above 0.30 are greedily matched from highest to lowest similarity, with each gold and predicted item used at most once. Development inspection selected the 0.30 threshold because it matched a genuine wording variation ("work on" versus "think about" trend watching) while excluding an observed unrelated webpage-email prediction at 0.278. Owner and due date are deliberately excluded from detection matching and are scored separately on matched items, avoiding double punishment for a slot error. This method and threshold must not change after held-out evaluation begins.

## Secondary metrics

- Owner accuracy on matched items.
- Due-date accuracy on matched items.
- Evidence-supported rate.
- Owner and due-date abstention rates.
- Average latency per transcript.
- Input and output tokens per transcript.
- Estimated API cost per transcript.

## Validity safeguards

- Freeze held-out labels before evaluating models.
- Do not tune the prompt on held-out failures.
- Keep the model identifier and decoding settings fixed.
- Report failure examples, not only averages.
- Treat the synthetic sample as a pipeline test, not evaluation data.
- Report AMI domain limitations and do not generalize results to all workplaces.
