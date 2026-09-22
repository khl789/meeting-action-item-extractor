# Final Experimental Results

## Experimental protocol

The dataset was divided into 20 development meetings and 20 held-out test meetings. The development set was used for prompt development and method selection. The held-out set contains 66 gold action items. Because the primary evaluation unit is the action item rather than the transcript, the primary test sample size is `n = 66`. The test set was evaluated only after the v13 prompt, model, temperature, evaluation matcher, and matching threshold had been frozen.

The final LLM system used `openai/gpt-5.6-luna` through OpenRouter with temperature 0. Detection used a frozen one-to-one matching rule. Text was lowercased and reduced to unique alphanumeric tokens. For every gold/prediction pair, the matcher calculated token-set Jaccard similarity for the action text and for the combined action-and-evidence text, retaining the higher score. Candidate pairs scoring at least 0.30 were greedily matched from highest to lowest score, and neither a gold item nor a prediction could be reused. Owner and due date were excluded from detection matching and evaluated separately on matched items. The rule-based method was evaluated as a baseline.

## Development-set results

| Method | Precision | Recall | F1 | Owner accuracy | Due-date accuracy | Evidence support |
|---|---:|---:|---:|---:|---:|---:|
| v11 | 0.762 | 0.653 | 0.703 | 0.750 | 0.844 | 0.738 |
| v12 | 0.673 | 0.755 | 0.712 | 0.784 | 0.757 | 0.927 |
| v13 | 0.814 | 0.714 | 0.761 | 0.714 | 0.971 | 0.907 |
| Rule baseline | 0.020 | 0.204 | 0.036 | 0.400 | 0.800 | 1.000 |

Version 13 achieved the highest development-set F1 score and was selected before inspecting final test performance.

## Held-out test results

| Method | Gold | Predicted | Matched | False positives | False negatives | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v13 | 66 | 56 | 41 | 15 | 25 | 0.732 | 0.621 | 0.672 |
| Rule baseline | 66 | 477 | 15 | 462 | 51 | 0.031 | 0.227 | 0.055 |

### Attribute and evidence results

| Method | Owner accuracy | Due-date accuracy | Evidence support |
|---|---:|---:|---:|
| v13 | 0.537 | 0.707 | 0.893 |
| Rule baseline | 0.533 | 0.667 | 1.000 |

Owner and due-date accuracy were calculated only on matched action items. Evidence support was calculated across predicted action items.

## Efficiency

For the 20 held-out test meetings, v13 used 215,522 tokens in total and cost USD 0.07739. The average cost was USD 0.00387 per meeting, and the average latency was 10.77 seconds per meeting.

For an illustrative business scenario, manual review is assumed to take 15 minutes per transcript and review of the evidence-linked extractor output is assumed to take 5 minutes. The estimated saving is therefore 10 project-manager minutes per transcript. At four transcripts per month, this would save about 40 minutes per month or 8 hours per year. These time figures are planning assumptions, not measured productivity results.

## Interpretation

The v13 system substantially outperformed the rule-based baseline. Its held-out F1 score was 0.672, compared with 0.055 for the baseline. The LLM system also reduced the number of false positives from 462 to 15.

Performance decreased from a development F1 of 0.761 to a held-out test F1 of 0.672, indicating a realistic generalisation gap. Evidence support remained stable at 0.893 on the test set. The largest remaining weaknesses were missed action items and owner identification, with test recall of 0.621 and owner accuracy of 0.537.

No prompt, model, extraction rule, matching rule, or threshold was modified after examining the held-out test results.

## Error analysis

Manual inspection of the lowest-scoring test meetings identified five recurring failure modes.

1. **Role descriptions treated as action items.** In `ES2006a` and `IS1007a`, the model extracted statements in which participants described their general project roles, such as industrial design, user-interface work, or marketing. Under the annotation policy, these broad role descriptions were not sufficiently concrete to count as confirmed meeting action items.

2. **Over-bundled actions.** In `ES2006a`, the model combined several responsibilities across multiple design stages into single long predictions. The gold annotations represented narrower tasks assigned by the project manager. This difference in granularity caused otherwise related text to remain unmatched.

3. **Failure to prioritise final explicit assignments.** The model sometimes relied on participants’ earlier descriptions of their roles instead of the project manager’s later allocation of concrete work. This contributed to both task-boundary and owner errors.

4. **Indirect collective commitments missed.** The collective request in `ES2006a` for all participants to think of unusual remote-control features was expressed in conversational language such as “take away with us” and “we all have a think”. The model did not identify it as a trackable group action.

5. **Over-filtering of valid self-commitments.** In `TS3007d`, the explicit statement “I'm going to finish my end report” was completely missed. This suggests that the conservative prompt can occasionally reject valid report-related tasks while attempting to exclude routine meeting administration.

A further evaluation limitation appeared in `IS1007a`. The prediction about thinking through technical points and discussing them at the next meeting was semantically related to the gold task of investigating how to obtain programme-content data, but the prediction omitted the central data-gathering detail and did not pass the frozen lexical similarity threshold. This is reported as a near miss rather than changing the matcher after test evaluation.

These errors indicate that future work should distinguish general roles from concrete commitments more reliably, preserve the original task granularity, prioritise explicit final assignments, and improve the handling of indirect group commitments and concise self-commitments.
