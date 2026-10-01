# Evaluation guide

## Purpose and evaluation unit

The evaluation tests whether the extractor identifies confirmed meeting action items and fills their owner and due-date fields without relying on unsupported information. The primary unit is the individual action item rather than the transcript. The held-out test split contains 20 meetings and 66 human-labelled action items, so the primary held-out sample size is `n = 66`.

## Gold labels and test separation

Gold files contain an action, owner, due date, and exact supporting quotation for every confirmed commitment or assignment. The annotation policy is defined in [`annotation-guide.md`](annotation-guide.md). The 20 development meetings were used for prompt development and method selection. The 20 test meetings were held out until prompt v13, the model, temperature, matching method, and matching threshold had been frozen.

## One-to-one detection matching

Predicted actions may express the same task using different wording, so exact string equality is not used for detection. The frozen matcher performs these steps:

1. Lowercase the text and retain unique alphanumeric tokens.
2. Calculate token-set Jaccard similarity for the gold and predicted action text.
3. Calculate the same similarity for their combined action and evidence text.
4. Keep the higher of the two similarity scores.
5. Retain candidate pairs scoring at least `0.30`.
6. Match candidates from highest to lowest score without reusing a gold item or prediction.

The threshold was selected using development examples and was not changed after the held-out evaluation. Owner and due date do not affect detection matching. They are evaluated separately on matched items, preventing one slot error from also becoming a detection error.

## Metrics

- **Precision** = matched predictions / all predictions. It measures false-positive control.
- **Recall** = matched predictions / all gold action items. It measures missed action items.
- **F1** is the harmonic mean of precision and recall and is the primary outcome metric.
- **Owner accuracy** is exact owner agreement across matched items.
- **Due-date accuracy** is exact due-date agreement across matched items.
- **Evidence support** is the proportion of predictions whose evidence quotation occurs in the source transcript.
- **Abstention rates** report how often the system returns `null` for owner or due date.
- **Efficiency metrics** include latency, token use, and estimated hosted-model cost per transcript.

The project set a detection F1 target of `0.80`. Other metrics were reported transparently without retroactively assigning numerical success thresholds.

## Running an evaluation

The following example evaluates a prediction file against the included synthetic smoke-test data:

```bash
PYTHONPATH=src python -m meeting_action_extractor evaluate \
  --gold data/sample/gold.json \
  --predictions outputs/model.json \
  --transcript data/sample/transcript.txt
```

The matching and metric implementation is in [`../src/meeting_action_extractor/evaluation.py`](../src/meeting_action_extractor/evaluation.py). The full frozen protocol is in [`experiment-plan.md`](experiment-plan.md), and the development and held-out results are in [`final-results.md`](final-results.md).

## Limitations

The lexical matcher is reproducible but imperfect. Semantically related tasks may fail to match when they use different words, while broad predictions may overlap with narrower gold items. Greedy matching is also sensitive to task granularity. Owner and due-date accuracy is calculated only on matched items, and the current evaluation does not separately measure whether every abstention was correct. The labels were produced by one annotator, so inter-annotator agreement was not measured. These limitations are reported rather than changing the matcher after viewing held-out results.
