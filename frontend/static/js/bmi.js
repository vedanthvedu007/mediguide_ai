/* ════════════════════════════════════════════════════════════
   MEDIGUIDE AI v3.0 — BMI Calculator
   bmi.js
════════════════════════════════════════════════════════════ */

function initBMI() {
  const heightSlider = document.getElementById('heightSlider');
  const weightSlider = document.getElementById('weightSlider');
  const ageDecBtn    = document.getElementById('ageDec');
  const ageIncBtn    = document.getElementById('ageInc');

  if (!heightSlider) return;

  heightSlider.addEventListener('input', () => {
    document.getElementById('heightVal').textContent = heightSlider.value;
    calcBMI();
  });
  weightSlider.addEventListener('input', () => {
    document.getElementById('weightVal').textContent = weightSlider.value;
    calcBMI();
  });
  if (ageDecBtn) {
    ageDecBtn.addEventListener('click', () => {
      if (currentAge > 1) { currentAge--; updateAgeDisplay(); calcBMI(); }
    });
  }
  if (ageIncBtn) {
    ageIncBtn.addEventListener('click', () => {
      if (currentAge < 120) { currentAge++; updateAgeDisplay(); calcBMI(); }
    });
  }

  // Initial calc
  calcBMI();
}

function updateAgeDisplay() {
  const el = document.getElementById('ageDisplay');
  if (el) el.textContent = currentAge;
}

function calcBMI() {
  const h = parseFloat(document.getElementById('heightSlider')?.value || 170);
  const w = parseFloat(document.getElementById('weightSlider')?.value || 65);

  const bmi = w / ((h / 100) ** 2);
  currentBMI = Math.round(bmi * 10) / 10;

  let category, desc, cls, adjust;
  if      (bmi < 18.5) { category = 'Underweight'; desc = 'Below healthy range — increase nutritious food intake'; cls = 'bmi-underweight'; adjust = 5; }
  else if (bmi < 25)   { category = 'Normal';      desc = 'Healthy weight for your height — keep it up!'; cls = 'bmi-normal'; adjust = 0; }
  else if (bmi < 30)   { category = 'Overweight';  desc = 'Slightly above healthy range — exercise and diet can help'; cls = 'bmi-overweight'; adjust = 10; }
  else                  { category = 'Obese';       desc = 'Significantly above healthy range — consult a doctor'; cls = 'bmi-obese'; adjust = 20; }

  currentBMICategory    = category;
  currentSeverityAdjust = adjust;

  // Update result card
  const resultCard = document.getElementById('bmiResultCard');
  if (resultCard) {
    resultCard.className = 'bmi-result-card ' + cls;
    document.getElementById('bmiNumber').textContent    = currentBMI.toFixed(1);
    document.getElementById('bmiCategory').textContent  = category;
    document.getElementById('bmiDesc').textContent      = desc;
  }

  // Update severity slider thumb
  const sevThumb = document.getElementById('sevThumb');
  if (sevThumb) {
    const pct = Math.min(Math.max(((bmi - 10) / 30) * 100, 0), 100);
    sevThumb.style.left = pct + '%';
  }

  // Update active row in table
  document.querySelectorAll('#bmiTable tr').forEach(row => row.classList.remove('active-row'));
  const catId = 'row_' + category.toLowerCase();
  const activeRow = document.getElementById(catId);
  if (activeRow) activeRow.classList.add('active-row');

  // Sync to report
  const rptBMI = document.getElementById('rptBMI');
  if (rptBMI) rptBMI.textContent = currentBMI.toFixed(1);
  const rptBMICat = document.getElementById('rptBMICat');
  if (rptBMICat) rptBMICat.textContent = category;
  const rptBMIBig = document.getElementById('rptBMIBig');
  if (rptBMIBig) rptBMIBig.textContent = currentBMI.toFixed(1);
  const rptBMICatBig = document.getElementById('rptBMICatBig');
  if (rptBMICatBig) rptBMICatBig.textContent = category;
  const rptBMIDetail = document.getElementById('rptBMIDetail');
  if (rptBMIDetail) rptBMIDetail.textContent = desc;
  const rptSevScore = document.getElementById('rptSevScore');
  if (rptSevScore) rptSevScore.textContent = `+${adjust} risk points`;

  // Sync profile panel
  const piBMI = document.getElementById('piBMI');
  if (piBMI) piBMI.textContent = `${currentBMI.toFixed(1)} (${category})`;
}

function chatWithBMI() {
  if (!currentBMI) { showToast('Please calculate your BMI first', 'warn'); return; }
  const msg = `My BMI is ${currentBMI.toFixed(1)} (${currentBMICategory}). Age: ${currentAge}. What health risks should I be aware of and what should I do?`;
  quickSend(msg);
}
