# Action-Item Annotation Guide

## Unit of annotation

Annotate one record for each confirmed future project task that is either assigned by one participant to another participant or explicitly stated by a participant as their own substantive project task. The evidence must be an exact transcript line that supports the record.

## Include

- A speaker assigns work to a named person: “Priya, please confirm the venue.”
- A direct request is accepted in the same local exchange.
- A participant, including the project manager, explicitly states their own substantive future project task: “I will test the prototype.”
- The group explicitly commits to a trackable future action, such as “We have to field-test it,” even if the individual owner remains `null`.

## Exclude

- Suggestions, brainstorming, wishes, and hypothetical work.
- Questions that do not create or confirm an assignment.
- Tasks already completed before the meeting.
- General goals without a concrete action.
- A participant merely states their own routine meeting-administration action, such as uploading minutes, rather than being assigned a trackable operation.
- A participant says they will explain or discuss something later in the current meeting; this is a conversational intention, not a trackable project task.
- An action explicitly described as being performed immediately in the current meeting, rather than follow-up work.
- An open-ended, recurring, or conditional promise to pass along information whenever it arrives, rather than a specific deliverable.
- A product requirement or design decision with no explicit assignee or employee commitment.
- Model-inferred owners or deadlines.

## Fields

- `action`: concise verb phrase preserving the meaning of the commitment.
- `owner`: exact transcript speaker label, such as `A/ID`, when supported; otherwise `null`. For a clearly shared task, join confirmed labels with ` + ` in transcript-label order, such as `A/ID + D/UI`.
- `due_date`: explicit date expression tied to the task in the evidence line or its immediately adjacent assignment exchange; otherwise `null`. A general statement about when the next meeting occurs is not a deadline unless it explicitly frames the assigned work.
- `evidence`: exact source line supporting the action item.
- `confidence`: reserved for system output; use `null` in human gold labels.

## Ambiguity policy

When a request and acceptance occur on different lines, use the clearest assignment line as evidence and consult the adjacent response during manual review. Record disagreements before changing the guide. Freeze the guide and held-out labels before final evaluation.
