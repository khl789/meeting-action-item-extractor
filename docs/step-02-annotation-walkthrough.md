# Step 2 Annotation Walkthrough

Use `data/processed/ES2002a/transcript.txt` and review the draft in `data/annotations/development/ES2002a.draft.json`.

## Decision test for every candidate

Answer these questions in order:

1. Is this future work rather than completed work?
2. Is it a confirmed commitment or assignment rather than a suggestion?
3. Is the action concrete enough to verify later?
4. Is the owner explicit or resolvable from the role mapping?
5. Is the deadline explicit in the local context?
6. Is the evidence copied exactly from the transcript?

If questions 1–3 are not all yes, remove the item. If question 4 or 5 is no, keep the action item but set that unsupported field to `null`.

## ES2002a judgement to review

The project manager says the next meeting is in thirty minutes, then assigns separate design, interface, and marketing work “inbetween now and then.” Human review decided that this context is not sufficiently explicit to label a due date. The three `due_date` fields therefore remain `null`. This conservative decision prevents the system from receiving credit for inferred deadlines.

Human review confirmed all three candidates as action items and rejected the inferred deadline. The reviewed labels are stored in `ES2002a.json`. Do not use `.draft.json` files in final evaluation.
