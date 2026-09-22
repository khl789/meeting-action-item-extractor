# Meeting Action Item Extractor

## Business and Technical Trade Off Analysis

### 1 Decision and problem context
I built a Meeting Action Item Extractor for project managers who must identify confirmed tasks, owners and deadlines without rereading an entire transcript. Existing products already address this workflow: [Otter generates action items, assigns them and links them to transcript content](https://help.otter.ai/hc/en-us/articles/5093228433687-Conversation-Page-Overview). I therefore do not claim the task is new. My contribution is a reproducible comparison between an LLM extractor and a rule baseline using fixed human labels and exact supporting evidence. Transcription, summarisation and automatic task execution remain outside scope.

### 2 Build versus buy architecture
I used a hybrid build-versus-buy architecture. I rented OpenRouter inference and fixed `openai/gpt-5.6-luna` at temperature zero. This avoided training, GPU provisioning and model serving for a four-week prototype, but created provider, network, model-access and per-use-cost dependencies. Meeting text leaves the local machine, so the prototype uses public AMI transcripts and a synthetic demo rather than confidential data.

I built the problem-specific Python layers: transcript parsing, prompt, JSON contract, deterministic validation, exact-evidence checking, rule baseline, data split and evaluation matcher. Each output records model, prompt version, token usage, latency and cost. The OpenRouter key stays in a local, version-control-excluded `.env` file.

The command-line tool remains the reproducible experimental interface. I rejected a low-code workflow because project-specific matching and auditable files require control. After evaluation, I added a lightweight local web interface for demonstration and human confirmation. It calls the same frozen pipeline and does not alter results.

### 3 Technical alternatives and design trade offs
I compared a deterministic rule extractor with a prompted foundation model. The baseline was cheap, local, fast and reproducible. Copying candidate sentences produced perfect evidence support, but keywords could not distinguish commitments from tentative discussion. It returned 477 predictions for 66 gold items: precision 0.031 and F1 0.055. Rules were unsuitable for semantic extraction but useful for schema and evidence validation.

The hosted model handled varied language better. Three prompt versions used only the 20-meeting development set. Version 13 had the highest development F1, 0.761, and was frozen before testing. It required no training and retained evidence, but introduced latency, cost, provider dependency and residual non-determinism.

I rejected RAG because the transcript supplies all valid evidence. I rejected agents because one input, model call and structured output suffice. Fine-tuning 49 development labels was unreliable. Prompting was cheaper and testable. The final hybrid used an LLM for semantics and deterministic code for validation, evidence checking and evaluation.

### 4 Data evaluation and experimental results
I used 40 scenario meetings from the [AMI Meeting Corpus](https://groups.inf.ed.ac.uk/ami/corpus/), whose manual transcripts are distributed under [CC BY 4.0](https://groups.inf.ed.ac.uk/ami/download/). Complete meetings were split into 20 development and 20 held-out meetings to prevent leakage.

Before evaluation, I fixed the annotation guide and labelled 115 action items: 49 development and 66 test. Each contained an action, owner, due date and exact quotation; unsupported slots were `null`. The action item, not transcript, was the primary unit, so held-out `n = 66`. Only development data informed v13 and the frozen matcher and 0.30 threshold.

The detector used one-to-one lexical matching. Text became unique lowercase alphanumeric tokens. For each gold/prediction pair, I retained the higher Jaccard similarity from action-only and combined action-evidence text. Pairs scoring at least 0.30 were greedily matched by descending score without reuse. Owner and due date were excluded and scored separately on matched items, preventing double penalties. This makes F1 falsifiable while preserving the pre-test rule.

On held-out data, v13 produced 56 items and matched 41: precision 0.732, recall 0.621 and F1 0.672 versus baseline F1 0.055. The 0.80 target was not achieved. Owner accuracy was 0.537, due-date accuracy 0.707 and evidence support 0.893. Owner abstention was 28.6% and due-date abstention 87.5%. Explicit deadlines were uncommon, but abstention correctness was not separately assessed. Nothing changed after viewing test results.

### 5 Business and operational implications
The observed operating cost was low: processing 20 held-out meetings cost USD 0.07739, or USD 0.00387 per transcript, with average latency of 10.77 seconds. At the same transcript length, model and price, 1,000 meetings would cost about USD 3.87 for inference. This estimate excludes transcription, storage, integration and human-review costs, and hosted-model prices may change.

For an illustrative Class 5 business-value scenario, I assume that manual review takes 15 minutes per transcript and that reviewing the extractor's evidence-linked output takes 5 minutes. The estimated saving is therefore 10 project-manager minutes per transcript, or about 67% of the initial review time. At four transcripts per month, this would save approximately 40 minutes per month or 8 hours per year, while the corresponding annual inference cost for 48 transcripts would be about USD 0.19. The time values are explicit planning assumptions, not measurements from a human time study.

This scenario can also be expressed as a decision formula: minutes saved per transcript equal manual review minutes minus assisted review minutes. The assumed ten-minute saving is not a performance result and should be replaced by timings in a pilot. Even if assisted review took ten rather than five minutes, the saving would be five minutes per transcript, or four hours annually at 48 transcripts. Financial value depends on the manager hourly rate and integration costs, so I do not claim an actual return. The calculation shows which measurements a pilot must collect: manual time, assisted time, correction effort, transcript volume and review quality.

The intended business value is faster triage rather than staff replacement. The extractor converts a long transcript into a short, evidence-linked review list. The illustrative calculation above expresses the potential value in project-manager minutes, but I did not run a human time study and therefore cannot claim measured productivity savings. Test F1 of 0.672, owner accuracy of 0.537 and 25 missed items show that automatic task creation would be unsafe. A project manager must confirm every item against its evidence before using it.

I would deploy the system only as decision support. Its low per-use cost makes experimentation practical, while human confirmation limits the impact of false positives, missed commitments and incorrect owners. Automatic scheduling or employee-performance assessment would require substantially stronger accuracy, privacy controls and monitoring.

### 6 Risks responsible use and recommendation
The main silent failure is a plausible-looking output that misses a real commitment or assigns it to the wrong person. I mitigate this by retaining an exact evidence quotation, returning `null` for unsupported fields and requiring project-manager confirmation before downstream use. The system must not create or evaluate employee tasks automatically.

A second risk is privacy because transcripts are sent to a hosted provider. I used only public AMI data and a synthetic demo. Production use would require participant notice, data minimisation, access control, retention limits and an approved provider agreement before confidential transcripts were processed.

A third limitation is representativeness. AMI scenario meetings focus on staged product-design discussions and may not reflect other organisations, meeting cultures or speaking styles. The labels also reflect one primary annotator, while lexical matching can mark reasonable paraphrases as errors. Future evaluation should use additional workplace domains, independent annotators and agreement measurement.

I recommend a limited human-in-the-loop pilot, not autonomous deployment. Success should require both improved recall and owner accuracy without reducing evidence support.
