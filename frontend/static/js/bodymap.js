/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — Interactive Body Map
   bodymap.js
════════════════════════════════════════════════════════════ */

function selectRegion(region) {
  selectedBodyRegion = region;
  selectedSymptoms   = [];

  // Highlight the selected hotspot on SVG
  document.querySelectorAll('.hotspot').forEach(el => {
    el.classList.toggle('active', el.dataset.region === region);
  });

  const names = {
    head:     '🧠 Head, Neck & Face',
    chest:    '🫀 Chest & Respiratory',
    abdomen:  '🫃 Abdomen & Stomach',
    back:     '🦴 Back & Spine',
    leftarm:  '💪 Left Arm & Hand',
    rightarm: '💪 Right Arm & Hand',
    legs:     '🦵 Legs & Feet',
    skin:     '🔴 Skin Issues'
  };

  const symptoms = REGION_SYMPTOMS[region] || [];

  const panel = document.getElementById('regionPanel');
  panel.innerHTML = `
    <div class="region-title">${names[region] || region}</div>
    <p style="font-size:13px;color:var(--text2);margin-bottom:16px">
      Select the symptoms you are experiencing in this area:
    </p>
    <div class="symptom-checkboxes" id="symCheckboxes">
      ${symptoms.map(s => `
        <label class="sym-check" id="sym_${s.id.replace(/\s/g,'_')}">
          <input type="checkbox" value="${s.id}" onchange="toggleSymptom('${s.id}')">
          ${s.label}
        </label>
      `).join('')}
    </div>

    <div class="severity-group">
      <div class="severity-group-label">How severe are these symptoms?</div>
      <div class="severity-btns">
        <button class="sev-btn" id="sev_mild" onclick="setSeverity('mild')">😊 Mild</button>
        <button class="sev-btn" id="sev_moderate" onclick="setSeverity('moderate')">😟 Moderate</button>
        <button class="sev-btn" id="sev_severe" onclick="setSeverity('severe')">😰 Severe</button>
      </div>
    </div>

    <button class="btn btn-primary btn-full" onclick="sendBodyMapSymptoms()" style="margin-top:8px">
      🩺 Check These Symptoms →
    </button>
  `;
}

function toggleSymptom(symptomId) {
  const label = document.getElementById('sym_' + symptomId.replace(/\s/g,'_'));
  if (selectedSymptoms.includes(symptomId)) {
    selectedSymptoms = selectedSymptoms.filter(s => s !== symptomId);
    if (label) label.classList.remove('checked');
  } else {
    selectedSymptoms.push(symptomId);
    if (label) label.classList.add('checked');
  }
}

function setSeverity(level) {
  selectedSeverity = level;
  document.querySelectorAll('.sev-btn').forEach(b => {
    b.className = 'sev-btn';
  });
  const map = { mild: 'mild-active', moderate: 'mod-active', severe: 'sev-active' };
  const el = document.getElementById('sev_' + level);
  if (el) el.classList.add(map[level]);
}

function sendBodyMapSymptoms() {
  if (!selectedSymptoms.length) {
    showToast('Please select at least one symptom first', 'warn');
    return;
  }
  const sevText = selectedSeverity ? ` (${selectedSeverity} severity)` : '';
  const msg = `I have ${selectedSymptoms.join(', ')} in my ${selectedBodyRegion} area${sevText}.`;
  quickSend(msg);
}
