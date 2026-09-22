# Prompt Development Record

Prompt changes were evaluated only on the three human-reviewed development meetings. No held-out test meeting was inspected during this process.

## v1

The first run on `ES2002a` detected all three action items, but inferred `Before the next meeting` for all three due dates. Detection F1 was 1.00 and due-date accuracy was 0.00.

## v2

The deadline rule was tightened: a due date must occur verbatim in the action evidence line, and contextual timing must not be converted into a deadline.

Across `ES2002a`, `IS1000a`, and `TS3005a`:

- Detection F1 was 1.00 for every meeting.
- Due-date accuracy was 1.00 for every meeting.
- Evidence-supported rate was 1.00 for every meeting.
- Owner accuracy was 1.00, 0.00, and 1.00 respectively. The ambiguous second-person assignments in `IS1000a` were safely left null.

## v3 (rejected)

The owner rule was relaxed to allow resolution from nearby dialogue. It did not improve aggregate owner accuracy. It also introduced one false positive in `TS3005a` and unsupported evidence in `ES2002a` and `TS3005a`. Macro detection F1 fell to approximately 0.95 and macro evidence-supported rate to approximately 0.81.

## v4 candidate

During human review of `ES2002b`, the task definition was clarified to include assignments from one participant to another and exclude unassigned self-statements such as the project manager saying they will upload meeting minutes. This clarification was made before any held-out model run. Prompt v4 encodes the same rule and must be re-evaluated only on development meetings before freezing.

## v5 candidate

The reviewer further clarified, before any held-out model run, that an employee's explicit statement of their own future project task is eligible. The exclusion applies to the project manager's self-stated routine meeting administration, such as uploading minutes. Prompt v5 supersedes v4 and must be evaluated only on development meetings before freezing.

## v6 candidate

Human review of `ES2002c` added two exclusions: intentions to continue explaining something later in the current meeting, and product requirements or design decisions that have no explicit assignee or employee commitment. Prompt v6 supersedes v5. This change was made without inspecting any held-out model output.

## v7 candidate

Human review of `ES2002d` clarified that a project manager's explicit commitment to substantive project work is eligible, while routine meeting administration remains excluded. Actions explicitly performed immediately during the current meeting are also excluded from follow-up action items. Prompt v7 supersedes v6, before any held-out model run.

## v8 candidate

Human review of `ES2005b` included a concrete group instruction to upload reports but excluded the project manager's open-ended conditional promise to forward targeted information whenever it arrives. Prompt v8 adds the requirement for a specific trackable deliverable. No held-out model output was inspected.

## v9 candidate

Human review of `ES2005c` confirmed a task with two clearly supported owners. Prompt v9 specifies the stable `LABEL + LABEL` representation for shared ownership and retains null for ambiguous group assignments. No held-out model output was inspected.

## v10 candidate

Human review of `IS1000c` clarified that an explicit deadline in the immediately adjacent assignment exchange applies when it directly frames the requested work, such as asking what work is needed for the next meeting. This remains distinct from merely announcing the next meeting time. Prompt v10 supersedes v9 before any held-out model output is inspected.

## v11 candidate

Human review of `IS1000d` included an explicit collective commitment to future field testing even though no individual owner was named. Prompt v11 includes trackable collective commitments and requires owner null when the participating individuals are unsupported. No held-out model output was inspected.

## Previous development choice

Prompt v2 was initially selected because it preserved perfect development-set action detection, due-date accuracy, and evidence support while abstaining on ambiguous owners. It is superseded by the v11 candidate after the human task-definition clarifications above. No held-out model result had been inspected.

## v11 full-development result

After all 20 development meetings were human reviewed, v11 was run once on the complete development split. Across 49 gold items, it predicted 42 items and the fixed v1 matcher reported 31 matches, 11 false positives, and 18 false negatives. Micro precision was 0.7381, recall was 0.6327, and F1 was 0.6813. The macro evidence-supported rate was 0.6550. Total hosted-model cost was USD 0.06558455 for 20 transcripts, with mean latency 7.8947 seconds.

Manual development-error inspection found that the model sometimes concatenated adjacent transcript lines, omitted individual tasks from bundled assignments, excluded a concrete one-time conditional deliverable, and used a bare acceptance as evidence instead of the line stating the task. No held-out model output was inspected.

## v12 candidate

Prompt v12 requires exactly one complete verbatim transcript line per evidence field, prohibits joined lines and ellipses, asks for every qualifying task in bundled assignments, distinguishes a concrete one-time conditional deliverable from an open-ended recurring promise, and prefers the action-bearing line over a bare acceptance. These changes respond only to development-set errors. The `TS3005c` development label was also made consistent with the established strict deadline rule: merely stating the time of the next meeting does not establish a due date.

## v13 candidate

Development inspection of v12 showed that “every separate qualifying task” caused coordinated responsibilities assigned to one owner in one line to be over-split. It also exposed work periods being mistaken for deadlines and a few broad objectives or actions already being performed during the meeting being treated as follow-up work. Prompt v13 preserves distinct assignments to different owners but keeps a coordinated same-owner list as one item, strengthens the exclusions for broad objectives and immediate actions, excludes work periods and start times from `due_date`, and explicitly requires disfluencies and repeated words to be copied verbatim. No held-out model output was inspected.

## Final development-set selection: v13

The final prompt was selected using only the 20-meeting development set. All versions were compared using the same frozen matching threshold of 0.30.

| Method | Predicted | Matched | Precision | Recall | F1 | Owner accuracy | Due-date accuracy | Evidence support |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v11 | 42 | 32 | 0.762 | 0.653 | 0.703 | 0.750 | 0.844 | 0.738 |
| v12 | 55 | 37 | 0.673 | 0.755 | 0.712 | 0.784 | 0.757 | 0.927 |
| v13 | 43 | 35 | 0.814 | 0.714 | 0.761 | 0.714 | 0.971 | 0.907 |
| Rule baseline | 500 | 10 | 0.020 | 0.204 | 0.036 | 0.400 | 0.800 | 1.000 |

Although v12 achieved slightly higher recall and owner accuracy, it produced substantially more false positives. Version 13 achieved the highest F1 score and precision while maintaining strong evidence support and due-date accuracy. Therefore, v13 was selected as the final prompt.

For v13, the total cost for 20 development meetings was USD 0.07285, the average cost was USD 0.00364 per meeting, and the average latency was 8.72 seconds per meeting.

The v13 prompt, model (`openai/gpt-5.6-luna`), temperature, evaluation matcher, and matching threshold are frozen before final held-out test evaluation. No component will be changed based on test-set results.