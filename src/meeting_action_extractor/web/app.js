const SAMPLE = `Maya: We need to finalize the launch checklist.
Daniel: I'll send the revised checklist by Friday.
Maya: Priya, could you confirm the venue tomorrow?
Priya: Yes, I will confirm it tomorrow.
Daniel: Maybe we should redesign the invitation later.
Maya: The budget was approved yesterday.`;

const transcript = document.querySelector('#transcript');
const method = document.querySelector('#method');
const extractButton = document.querySelector('#extractButton');
const sampleButton = document.querySelector('#sampleButton');
const emptyState = document.querySelector('#emptyState');
const loadingState = document.querySelector('#loadingState');
const results = document.querySelector('#results');
const errorState = document.querySelector('#errorState');
const itemCount = document.querySelector('#itemCount');

transcript.value = SAMPLE;
sampleButton.addEventListener('click', () => { transcript.value = SAMPLE; transcript.focus(); });

function show(name) {
  [emptyState, loadingState, results, errorState].forEach((el) => el.classList.add('hidden'));
  name.classList.remove('hidden');
}

function safe(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[character]);
}

function render(payload) {
  const checks = payload.validation || [];
  const items = payload.action_items || [];
  itemCount.textContent = `${items.length} item${items.length === 1 ? '' : 's'}`;
  if (!items.length) {
    results.innerHTML = '<div class="empty-state"><div class="empty-icon">0</div><h3>No confirmed commitments</h3><p>The extractor did not find a supported future action in this transcript.</p></div>';
  } else {
    results.innerHTML = items.map((item, index) => {
      const confidence = item.confidence == null ? 'Not scored' : `${Math.round(item.confidence * 100)}%`;
      const supported = checks[index]?.evidence_supported ? '<span class="supported">✓ exact quote</span>' : 'Review needed';
      return `<section class="item">
        <p class="item-number">ACTION ITEM ${String(index + 1).padStart(2, '0')}</p>
        <h3>${safe(item.action)}</h3>
        <div class="fields">
          <div class="field"><span>OWNER</span><b>${safe(item.owner || 'Not specified')}</b></div>
          <div class="field"><span>DUE DATE</span><b>${safe(item.due_date || 'Not specified')}</b></div>
          <div class="field"><span>CONFIDENCE</span><b>${safe(confidence)}</b></div>
        </div>
        <p class="evidence"><b>EVIDENCE · ${supported}</b><br>${safe(item.evidence)}</p>
      </section>`;
    }).join('');
  }
  show(results);
}

extractButton.addEventListener('click', async () => {
  extractButton.disabled = true;
  itemCount.textContent = 'Processing';
  show(loadingState);
  try {
    const response = await fetch('/api/extract', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({transcript: transcript.value, method: method.value})
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'The extractor could not complete this request.');
    render(payload);
  } catch (error) {
    itemCount.textContent = 'Error';
    errorState.innerHTML = `<b>Could not extract action items.</b><br>${safe(error.message)}`;
    show(errorState);
  } finally {
    extractButton.disabled = false;
  }
});
