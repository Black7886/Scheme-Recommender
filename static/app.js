// Core Frontend Application Logic for NSFDC Concessional Loan Scheme Portal

let currentStep = 1;
const maxStep = 10;
let currentLanguage = 'en';

// Wizard Form State
const wizardState = {
  purpose: 'micro_business',
  gender: 'male',
  loan_amount: 100000,
  family_income: 250000,
  education_status: 'undergraduate',
  recommended_scheme: null,
  applicable_interest_rate: 6.5,
  calculated_emi: 0.0,
  tenure_months: 36,
  moratorium_months: 3,
  chosen_mode: 'offline', // online / offline
  selected_partner: null,
  application_no: 'NSFDC-' + Math.random().toString(36).substr(2, 8).toUpperCase()
};

// Leaflet Map instance
let partnerMap = null;
let mapMarkers = [];

document.addEventListener('DOMContentLoaded', () => {
  renderStepProgress();
  setLanguage('en');
  selectPurpose('micro_business');
  selectGender('male');
  updateStepVisibility();
});

// Font Resizer
let currentFontSizeLevel = 0;
function changeFontSize(delta) {
  currentFontSizeLevel += delta;
  if (currentFontSizeLevel > 2) currentFontSizeLevel = 2;
  if (currentFontSizeLevel < -1) currentFontSizeLevel = -1;
  
  const baseSize = 16 + (currentFontSizeLevel * 2);
  document.body.style.fontSize = baseSize + 'px';
}

// 100% Language Switching Engine
function setLanguage(langCode) {
  currentLanguage = langCode;
  document.getElementById('globalLangSelect').value = langCode;
  document.getElementById('s1_lang_select').value = langCode;

  const dict = translations[langCode] || translations['en'];

  // Iterate over translation keys and update element text content
  for (const key in dict) {
    // Update elements with ID `t_<key>`
    const el = document.getElementById(`t_${key}`);
    if (el) {
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = dict[key];
      } else {
        el.textContent = dict[key];
      }
    }
  }

  // Update dynamic scheme & story cards if already loaded
  if (wizardState.recommended_scheme) {
    renderMatchedSchemeDetails();
    loadCommunityPosts(wizardState.recommended_scheme.code);
  }
}

// Render Step Progress Dots
function renderStepProgress() {
  const container = document.getElementById('stepIndicatorsGrid');
  let html = '';
  for (let i = 1; i <= maxStep; i++) {
    const activeClass = i === currentStep ? 'active' : (i < currentStep ? 'completed' : '');
    html += `<div class="step-dot ${activeClass}">${i}</div>`;
  }
  container.innerHTML = html;

  const percent = (currentStep / maxStep) * 100;
  document.getElementById('progressBarFill').style.width = `${percent}%`;
}

// Update Step Visibility & Navigation Buttons
function updateStepVisibility() {
  for (let i = 1; i <= maxStep; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) {
      el.style.display = i === currentStep ? 'block' : 'none';
    }
  }

  renderStepProgress();

  // Navigation Button Controls
  const prevBtn = document.getElementById('btnPrevStep');
  const nextBtn = document.getElementById('btnNextStep');

  if (prevBtn) prevBtn.style.display = currentStep > 1 ? 'inline-block' : 'none';

  if (nextBtn) {
    if (currentStep === maxStep) {
      nextBtn.style.display = 'none';
    } else {
      nextBtn.style.display = 'inline-block';
      const dict = translations[currentLanguage] || translations['en'];
      nextBtn.textContent = dict.next_btn || 'Continue to Next Step →';
    }
  }

  // Trigger Step Specific Actions
  if (currentStep === 6) {
    fetchSchemeRecommendation();
  } else if (currentStep === 8) {
    runEMICalculator();
  } else if (currentStep === 9) {
    setTimeout(initPartnerMap, 200);
  } else if (currentStep === 10) {
    renderFinalSummary();
  }
}

// Step Navigation with Strict Sequence Validation (NO SKIP ALLOWED)
function nextStep() {
  // Validate current step before advancing
  if (currentStep === 2 && !wizardState.purpose) {
    alert(translations[currentLanguage]?.no_skip_alert || 'Please select a loan purpose before continuing.');
    return;
  }
  if (currentStep === 3 && !wizardState.gender) {
    alert(translations[currentLanguage]?.no_skip_alert || 'Please select gender before continuing.');
    return;
  }
  if (currentStep === 4) {
    const amt = parseFloat(document.getElementById('input_loan_amount').value);
    if (!amt || amt < 10000) {
      alert('Please enter a valid loan amount (Minimum ₹10,000).');
      return;
    }
    wizardState.loan_amount = amt;
  }
  if (currentStep === 5) {
    const inc = parseFloat(document.getElementById('input_family_income').value);
    if (!inc) {
      alert('Please enter valid annual family income.');
      return;
    }
    wizardState.family_income = inc;
    wizardState.education_status = document.getElementById('select_edu_status').value;
  }

  if (currentStep < maxStep) {
    currentStep++;
    updateStepVisibility();
    window.scrollTo({ top: document.getElementById('wizard-anchor').offsetTop - 50, behavior: 'smooth' });
  }
}

function prevStep() {
  if (currentStep > 1) {
    currentStep--;
    updateStepVisibility();
    window.scrollTo({ top: document.getElementById('wizard-anchor').offsetTop - 50, behavior: 'smooth' });
  }
}

function jumpToStep(stepNum) {
  // Allow direct navigation to completed or earlier steps
  currentStep = stepNum;
  updateStepVisibility();
}

// Option Card Selections (Step 2 & Step 3)
function selectPurpose(purposeKey) {
  wizardState.purpose = purposeKey;
  
  // Reset all Step 2 option cards
  document.querySelectorAll('#step-2 .option-card').forEach(el => {
    el.classList.remove('selected');
    el.style.border = '2px solid #E2E8F0';
    el.style.backgroundColor = '#FFFFFF';
  });
  document.querySelectorAll('#step-2 .selected-indicator').forEach(el => el.style.display = 'none');

  const cardMap = {
    'new_business': { cardId: 'opt_purpose_new_business', badgeId: 't_selected_p1' },
    'expand_business': { cardId: 'opt_purpose_expand_business', badgeId: 't_selected_p2' },
    'machinery_tools': { cardId: 'opt_purpose_machinery_tools', badgeId: 't_selected_p3' },
    'education': { cardId: 'opt_purpose_education', badgeId: 't_selected_p4' },
    'artisan_craft': { cardId: 'opt_purpose_artisan_craft', badgeId: 't_selected_p5' },
    'green_vehicle': { cardId: 'opt_purpose_green_vehicle', badgeId: 't_selected_p6' }
  };

  const target = cardMap[purposeKey];
  if (target) {
    const card = document.getElementById(target.cardId);
    const badge = document.getElementById(target.badgeId);
    if (card) {
      card.classList.add('selected');
      card.style.border = '2px solid #1D4ED8';
      card.style.backgroundColor = '#EFF6FF';
    }
    if (badge) badge.style.display = 'block';
  }
}

function selectGender(genderKey) {
  wizardState.gender = genderKey;
  document.querySelectorAll('#step-3 .option-card').forEach(el => el.classList.remove('selected'));
  
  if (genderKey === 'male') document.getElementById('opt_gender_male').classList.add('selected');
  else if (genderKey === 'female') document.getElementById('opt_gender_female').classList.add('selected');
  else if (genderKey === 'other') document.getElementById('opt_gender_other').classList.add('selected');
}

function updateLoanAmountSlider(val) {
  document.getElementById('slider_loan_amount').value = val;
  wizardState.loan_amount = parseFloat(val);
}

function updateLoanAmountInput(val) {
  document.getElementById('input_loan_amount').value = val;
  wizardState.loan_amount = parseFloat(val);
}

// STEP 6: Fetch Scheme Recommendation from Backend Rule Engine
function fetchSchemeRecommendation() {
  fetch('/api/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      purpose: wizardState.purpose,
      gender: wizardState.gender,
      loan_amount: wizardState.loan_amount,
      family_income: wizardState.family_income,
      education_status: wizardState.education_status
    })
  })
  .then(res => res.json())
  .then(data => {
    wizardState.recommended_scheme = data.recommended_scheme;
    wizardState.applicable_interest_rate = data.applicable_interest_rate;
    
    // Set calculator default tenure & moratorium from scheme
    wizardState.tenure_months = data.recommended_scheme.max_tenure_years * 12;
    wizardState.moratorium_months = data.recommended_scheme.moratorium_months;

    renderMatchedSchemeDetails();
    loadCommunityPosts(data.recommended_scheme.code);
  });
}

function renderMatchedSchemeDetails() {
  const scheme = wizardState.recommended_scheme;
  if (!scheme) return;

  const isHindi = currentLanguage === 'hi';
  document.getElementById('res_scheme_name').textContent = isHindi ? scheme.name_hi : scheme.name_en;
  
  const matchReason = isHindi ? scheme.description_hi : scheme.description_en;
  document.getElementById('res_match_reason').textContent = matchReason;

  document.getElementById('res_max_loan').textContent = `₹${scheme.max_amount.toLocaleString('en-IN')}`;
  document.getElementById('res_interest_rate').textContent = `${wizardState.applicable_interest_rate}% p.a.`;
  document.getElementById('res_moratorium').textContent = `${scheme.moratorium_months} Months`;
  document.getElementById('res_max_tenure').textContent = `${scheme.max_tenure_years} Years`;

  document.getElementById('res_cost_sharing').textContent = scheme.cost_sharing_rule;
  document.getElementById('res_eligibility').textContent = isHindi ? scheme.eligibility_hi : scheme.eligibility_en;
  document.getElementById('res_documents').textContent = isHindi ? scheme.documents_hi : scheme.documents_en;

  // Set default calculator values in Step 8
  document.getElementById('calc_principal').value = wizardState.loan_amount;
  document.getElementById('calc_rate').value = wizardState.applicable_interest_rate;
  document.getElementById('calc_tenure_years').value = scheme.max_tenure_years;
  document.getElementById('calc_moratorium_months').value = scheme.moratorium_months;

  // Set online application link in Step 9
  document.getElementById('btn_external_portal_link').href = scheme.online_apply_url || 'https://jansamarth.in/';
}

// STEP 7: Load Community Success Stories
function loadCommunityPosts(schemeCode) {
  fetch(`/api/community-posts/${schemeCode}`)
  .then(res => res.json())
  .then(posts => {
    const container = document.getElementById('communityPostsGrid');
    const isHindi = currentLanguage === 'hi';

    if (!posts || posts.length === 0) {
      container.innerHTML = `<p style="color:#64748B;">Community success stories loading...</p>`;
      return;
    }

    container.innerHTML = posts.map(p => `
      <div class="community-card">
        <img src="${p.image_url}" alt="${p.beneficiary_name_en}">
        <div class="community-card-body">
          <span class="badge-impact">${isHindi ? p.impact_badge_hi : p.impact_badge_en}</span>
          <h4>${isHindi ? p.beneficiary_name_hi : p.beneficiary_name_en}</h4>
          <p style="font-size:0.82rem; color:#64748B; margin: 2px 0 8px 0;">📍 ${isHindi ? p.location_hi : p.location_en} | 💼 ${isHindi ? p.business_type_hi : p.business_type_en}</p>
          <p style="font-size:0.88rem; color:#334155;">"${isHindi ? p.story_hi : p.story_en}"</p>
          <strong style="color:var(--gov-blue-primary); font-size:0.9rem;">Loan Amount: ₹${p.loan_amount.toLocaleString('en-IN')}</strong>
        </div>
      </div>
    `).join('');
  });
}

// STEP 8: Financial EMI Calculator
function runEMICalculator() {
  const principal = parseFloat(document.getElementById('calc_principal').value || wizardState.loan_amount);
  const rate = parseFloat(document.getElementById('calc_rate').value || wizardState.applicable_interest_rate);
  const years = parseInt(document.getElementById('calc_tenure_years').value || 3);
  const moraMonths = parseInt(document.getElementById('calc_moratorium_months').value || 3);

  fetch('/api/calculate-emi', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      principal: principal,
      annual_rate: rate,
      tenure_months: years * 12,
      moratorium_months: moraMonths
    })
  })
  .then(res => res.json())
  .then(data => {
    wizardState.calculated_emi = data.monthly_emi;
    wizardState.loan_amount = principal;

    document.getElementById('res_emi_val').textContent = `₹${data.monthly_emi.toLocaleString('en-IN')}`;
    document.getElementById('res_interest_val').textContent = `₹${data.total_interest.toLocaleString('en-IN')}`;
    document.getElementById('res_repayable_val').textContent = `₹${data.total_repayable.toLocaleString('en-IN')}`;

    const isHindi = currentLanguage === 'hi';
    document.getElementById('res_plain_summary').textContent = isHindi ? data.summary_hi : data.summary_en;
  });
}

// STEP 9: Geo-Spatial Partner Locator & Mode Selection
let userLiveCoords = { lat: null, lng: null };
let userLiveMarker = null;

function setAppMode(mode) {
  wizardState.chosen_mode = mode;
  document.getElementById('view_mode_online').style.display = mode === 'online' ? 'block' : 'none';
  document.getElementById('view_mode_offline').style.display = mode === 'offline' ? 'block' : 'none';

  if (mode === 'offline') {
    setTimeout(initPartnerMap, 100);
  }
}

function initPartnerMap() {
  const mapContainer = document.getElementById('map');
  if (!mapContainer) return;

  if (!partnerMap) {
    // Default center on India
    partnerMap = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap contributors | NSFDC Geo-Spatial Locator'
    }).addTo(partnerMap);
  }

  // Attempt auto geolocation or load default nearest partners
  if (navigator.geolocation && !userLiveCoords.lat) {
    getLiveUserLocation();
  } else {
    fetchChannelPartners();
  }
}

// Live GPS Location Detection
function getLiveUserLocation() {
  const statusEl = document.getElementById('liveLocationStatus');
  if (statusEl) {
    statusEl.style.display = 'block';
    statusEl.textContent = '📡 Requesting GPS Live Location access...';
  }

  if (!navigator.geolocation) {
    alert('Geolocation is not supported by your browser. You can search by City or Pincode.');
    fetchChannelPartners();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      userLiveCoords.lat = lat;
      userLiveCoords.lng = lng;

      if (statusEl) {
        statusEl.innerHTML = `📍 Live Location Detected: <strong>${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E</strong>. Showing nearest active Public Sector Banks & Channel Partners sorted by distance!`;
      }

      if (partnerMap) {
        partnerMap.setView([lat, lng], 11);

        // Place red user live marker
        if (userLiveMarker) partnerMap.removeLayer(userLiveMarker);
        const userIcon = L.divIcon({
          className: 'user-live-pin',
          html: '<div style="background:#EF4444; color:#fff; border:2px solid #fff; border-radius:50%; width:28px; height:28px; text-align:center; line-height:24px; font-size:14px; font-weight:bold; box-shadow:0 0 10px rgba(239,68,68,0.9);">📍</div>',
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });
        userLiveMarker = L.marker([lat, lng], { icon: userIcon }).addTo(partnerMap);
        userLiveMarker.bindPopup('<strong>📍 YOUR LIVE LOCATION</strong><br>Sorted nearest bank branches relative to you.').openPopup();
      }

      fetchChannelPartners('', lat, lng);
    },
    (error) => {
      console.warn('Geolocation error:', error.message);
      if (statusEl) {
        statusEl.innerHTML = `⚠️ GPS Location Permission Denied or Unavailable. Showing all authorized Channel Partner banks in India. (Use search box below to filter by city/pincode).`;
      }
      fetchChannelPartners();
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
}

function fetchChannelPartners(pincodeOrCity = '', lat = null, lng = null) {
  const schemeCode = wizardState.recommended_scheme ? wizardState.recommended_scheme.code : '';
  
  const targetLat = lat || userLiveCoords.lat;
  const targetLng = lng || userLiveCoords.lng;

  let url = `/api/partners?`;
  if (schemeCode) url += `scheme_code=${schemeCode}&`;
  if (pincodeOrCity) url += `search=${encodeURIComponent(pincodeOrCity)}&`;
  if (targetLat && targetLng) url += `lat=${targetLat}&lng=${targetLng}&`;

  fetch(url)
  .then(res => res.json())
  .then(partners => {
    renderPartnerListAndMarkers(partners);
  })
  .catch(err => {
    console.error('Failed to load channel partners:', err);
    // Fallback fetch all active partners
    fetch('/api/partners')
    .then(r => r.json())
    .then(data => renderPartnerListAndMarkers(data));
  });
}

function renderPartnerListAndMarkers(partners) {
  const container = document.getElementById('bankListContainer');
  const isHindi = currentLanguage === 'hi';

  // Clear existing markers (except live user marker)
  mapMarkers.forEach(m => partnerMap.removeLayer(m));
  mapMarkers = [];

  if (!partners || partners.length === 0) {
    container.innerHTML = `<div style="background:#FFFBEB; border:1px solid #FCD34D; padding:15px; border-radius:6px; color:#92400E;">
      <strong>No bank branches found for this search filter.</strong><br>
      <small>Showing all available authorized Public Sector Banks in India below.</small>
    </div>`;
    // Fallback fetch all
    fetch('/api/partners')
    .then(r => r.json())
    .then(allPartners => {
      if (allPartners && allPartners.length > 0) renderPartnerListAndMarkers(allPartners);
    });
    return;
  }

  container.innerHTML = partners.map(p => `
    <div class="bank-card ${wizardState.selected_partner && wizardState.selected_partner.id === p.id ? 'selected' : ''}" id="partner_card_${p.id}">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <h4 style="margin:0 0 4px 0; color:var(--gov-blue-dark); font-size:1.05rem;">${isHindi ? p.name_hi : p.name_en}</h4>
        ${p.distance_km !== null ? `<span style="background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.78rem;">📍 ${p.distance_km} km away</span>` : ''}
      </div>
      <div style="margin: 4px 0 8px 0; display:flex; gap:6px;">
        <span style="background:#FEF3C7; color:#92400E; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.78rem;">🏛️ ${p.partner_type}</span>
        <span style="background:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.78rem;">✓ Eligible Partner</span>
      </div>
      <p style="margin:0 0 6px 0; font-size:0.88rem; font-weight:600; color:#0284C7;">${isHindi ? p.branch_name_hi : p.branch_name_en}</p>
      <p style="margin:0 0 6px 0; font-size:0.85rem; color:#475569;">📍 ${isHindi ? p.address_hi : p.address_en}, ${p.pincode}</p>
      <p style="margin:0 0 10px 0; font-size:0.85rem; color:#475569;">📞 ${p.contact_number} | ✉️ ${p.email}</p>
      <button class="btn-primary" style="padding: 7px 16px; font-size:0.85rem;" onclick="selectPartnerBank(${p.id})">
        ${wizardState.selected_partner && wizardState.selected_partner.id === p.id ? 'Selected Channel Partner ✓' : 'Select This Bank Branch'}
      </button>
    </div>
  `).join('');

  // Add markers to map
  partners.forEach(p => {
    const marker = L.marker([p.latitude, p.longitude]).addTo(partnerMap);
    marker.bindPopup(`
      <strong style="color:#003366;">${isHindi ? p.name_hi : p.name_en}</strong><br>
      <b>${isHindi ? p.branch_name_hi : p.branch_name_en}</b> (${p.partner_type})<br>
      📍 ${p.address_en}, ${p.pincode}<br>
      📞 ${p.contact_number}<br>
      ${p.distance_km !== null ? `<span style="color:#1E40AF; font-weight:bold;">Distance: ${p.distance_km} km away</span>` : ''}
    `);
    mapMarkers.push(marker);
  });
}

function searchBanksByLocation() {
  const query = document.getElementById('input_search_pincode').value.trim();
  fetchChannelPartners(query, userLiveCoords.lat, userLiveCoords.lng);
}

function selectPartnerBank(partnerId) {
  fetch('/api/partners')
  .then(res => res.json())
  .then(partners => {
    const p = partners.find(x => x.id === partnerId);
    if (p) {
      wizardState.selected_partner = p;
      renderPartnerListAndMarkers(partners);
      alert(`Selected Channel Partner Branch: ${p.name_en} - ${p.branch_name_en}`);
    }
  });
}

// STEP 10: Render Final Summary
function renderFinalSummary() {
  document.getElementById('sum_app_no').textContent = wizardState.application_no;
  
  const purposeName = wizardState.purpose === 'micro_business' ? 'Micro Business / Self-Employment' : 
                      (wizardState.purpose === 'education' ? 'Higher Education' : 'Medium Business / Machinery');
  document.getElementById('sum_purpose_amount').textContent = `${purposeName} (₹${wizardState.loan_amount.toLocaleString('en-IN')})`;

  const scheme = wizardState.recommended_scheme;
  document.getElementById('sum_scheme_name').textContent = scheme ? scheme.name_en : 'NSFDC Concessional Loan Scheme';
  document.getElementById('sum_rate_tenure').textContent = `${wizardState.applicable_interest_rate}% p.a. | Tenure: ${scheme ? scheme.max_tenure_years : 3} Years`;
  
  document.getElementById('sum_calculated_emi').textContent = `₹${wizardState.calculated_emi.toLocaleString('en-IN')} / month (After ${scheme ? scheme.moratorium_months : 3}-month Moratorium)`;
  document.getElementById('sum_chosen_mode').textContent = wizardState.chosen_mode === 'online' ? 'Online Application Pathway (Direct Portal)' : 'Offline Channel Partner Visit';

  const partner = wizardState.selected_partner;
  document.getElementById('sum_selected_bank').textContent = partner ? `${partner.name_en} - ${partner.branch_name_en} (${partner.address_en}, ${partner.pincode})` : 'State Bank of India - Main Branch, Connaught Place, New Delhi';
}

function submitFinalApplication() {
  fetch('/api/applications', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      applicant_name: 'SC Citizen Applicant',
      gender: wizardState.gender,
      loan_purpose: wizardState.purpose,
      required_amount: wizardState.loan_amount,
      annual_income: wizardState.family_income,
      education_status: wizardState.education_status,
      recommended_scheme_code: wizardState.recommended_scheme ? wizardState.recommended_scheme.code : 'MICRO',
      calculated_emi: wizardState.calculated_emi,
      tenure_months: wizardState.tenure_months,
      moratorium_months: wizardState.moratorium_months,
      chosen_mode: wizardState.chosen_mode,
      selected_partner_id: wizardState.selected_partner ? wizardState.selected_partner.id : 1
    })
  })
  .then(res => res.json())
  .then(data => {
    alert(`${data.message_en}\nReference Guidance No: ${data.application_no}`);
  });
}
