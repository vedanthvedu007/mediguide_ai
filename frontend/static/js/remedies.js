/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Home Remedies Panel
   remedies.js
════════════════════════════════════════════════════════════ */

let activeRemedyFilter = 'all';

function initRemedies() {
  renderRemedyCards('all');
}

function filterRemedies(category) {
  activeRemedyFilter = category;

  // Update filter chip active state
  document.querySelectorAll('.filter-chip').forEach(el => {
    el.classList.toggle('active', el.dataset.cat === category);
  });

  renderRemedyCards(category);
}

function renderRemedyCards(category) {
  const grid = document.getElementById('remediesGrid');
  if (!grid) return;

  const filtered = category === 'all'
    ? REMEDY_DATA
    : REMEDY_DATA.filter(r => r.category === category);

  if (!filtered.length) {
    grid.innerHTML = `
      <div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--text3)">
        <div style="font-size:48px;margin-bottom:12px">🌿</div>
        <p>No remedies in this category yet.</p>
      </div>`;
    return;
  }

  grid.innerHTML = filtered.map(r => `
    <div class="remedy-card animate-fadein">
      <div class="remedy-card-header">
        <div class="remedy-card-icon">${r.icon}</div>
        <div>
          <div class="remedy-card-title">${r.title}</div>
          <div class="remedy-card-category">${r.category}</div>
        </div>
      </div>
      <div class="remedy-card-body">
        <div class="remedy-steps">
          ${r.steps.slice(0, 5).map((step, i) => `
            <div class="remedy-step">
              <div class="step-num">${i + 1}</div>
              <span>${step}</span>
            </div>
          `).join('')}
        </div>
        ${r.escalate ? `<div class="remedy-escalate">${r.escalate}</div>` : ''}
      </div>
      <div class="remedy-card-footer">
        <button class="send-to-chat-btn" onclick="sendRemedyToChat('${r.id}')">
          💬 Ask AI about this &rarr;
        </button>
      </div>
    </div>
  `).join('');
}

function sendRemedyToChat(remedyId) {
  const remedy = REMEDY_DATA.find(r => r.id === remedyId);
  if (!remedy) return;
  const msg = `I am looking for more information and advice about: ${remedy.title}. ${remedy.steps[0]}`;
  quickSend(msg);
}
